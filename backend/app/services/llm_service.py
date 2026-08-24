import json
import logging
import re
from typing import Dict, Any, Optional, Tuple
import httpx
from app.config import settings
from app.schemas.analysis import CandidateAnalysisOutput

logger = logging.getLogger(__name__)

SCREENER_SYSTEM_PROMPT = """You are an expert technical recruiter and AI talent screener.
Your task is to evaluate a candidate's resume against a Job Description (JD) with high precision, fairness, and semantic understanding.

CRITICAL RULES:
1. Return ONLY a valid, parseable JSON object matching the exact schema specified below.
2. Do NOT output markdown code blocks (```json), commentary, or extra text.
3. Perform true semantic matching (e.g. "ML" = "Machine Learning", "PostgreSQL" = "SQL Database experience", "FastAPI" = "Python REST API").
4. Do NOT falsely invent skills, years, or credentials that the candidate does not have.
5. If a candidate is missing a required skill, list it in skills_match.missing.
6. Provide an honest, calibrated overall score from 1.0 to 10.0:
   - 8.0 - 10.0: Strong Match (exceeds or meets all mandatory requirements)
   - 6.5 - 7.9: Match (solid fit, minor gaps in non-critical areas)
   - 4.5 - 6.4: Partial Match (has transferable skills but lacks key requirements)
   - 1.0 - 4.4: Weak Match (misaligned role or significant missing core requirements)

JSON SCHEMA:
{
  "candidate_name": "<Candidate Full Name or Unknown Candidate>",
  "overall_score": <Float 1.0 - 10.0>,
  "recommendation": "<Strong Match | Match | Partial Match | Weak Match>",
  "skills_match": {
    "matched": ["<skill1>", "<skill2>"],
    "partial": ["<skill3>"],
    "missing": ["<skill4>"]
  },
  "experience_match": {
    "score": <Float 0.0 - 10.0>,
    "summary": "<1-2 sentence analysis of relevant work experience>"
  },
  "education_match": {
    "score": <Float 0.0 - 10.0>,
    "summary": "<1-2 sentence assessment of education and credentials>"
  },
  "relevant_projects": ["<Project name and domain relevance summary>"],
  "strengths": ["<Specific verified strength 1>", "<Specific verified strength 2>"],
  "gaps": ["<Specific verified gap or missing requirement 1>", "<Specific gap 2>"],
  "justification": "<Concise 2-3 sentence executive recruiter justification explaining WHY this score was assigned>"
}
"""


class LLMService:
    """OpenAI-compatible client with JSON schema enforcement, retries, and fallback."""

    @classmethod
    async def analyze_candidate(
        cls,
        candidate_data: Dict[str, Any],
        jd_requirements: Dict[str, Any],
        raw_resume_text: str,
        raw_jd_text: str
    ) -> Tuple[Optional[CandidateAnalysisOutput], str]:
        """
        Executes semantic analysis via OpenAI-compatible endpoint.
        Returns: (Validated CandidateAnalysisOutput or None, evaluation_mode: 'llm' | 'heuristic_fallback')
        """
        # If API key is not configured, gracefully use heuristic fallback
        if not settings.OPENAI_API_KEY or len(settings.OPENAI_API_KEY.strip()) < 5:
            logger.info("OPENAI_API_KEY is not configured. Utilizing high-fidelity semantic fallback evaluator.")
            return None, "heuristic_fallback"

        user_prompt = cls._build_user_prompt(candidate_data, jd_requirements, raw_resume_text, raw_jd_text)

        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": SCREENER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"} if "gpt" in settings.OPENAI_MODEL.lower() else None
        }

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY.strip()}",
            "Content-Type": "application/json"
        }

        endpoint = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"

        for attempt in range(1, settings.LLM_MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
                    response = await client.post(endpoint, json=payload, headers=headers)

                if response.status_code != 200:
                    logger.warning(f"LLM API returned status {response.status_code}: {response.text[:200]}")
                    continue

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Parse and validate JSON
                parsed_json = cls._extract_and_repair_json(content)
                if parsed_json:
                    validated = CandidateAnalysisOutput(**parsed_json)
                    return validated, "llm"

            except httpx.TimeoutException:
                logger.warning(f"LLM request timed out on attempt {attempt}/{settings.LLM_MAX_RETRIES}")
            except Exception as e:
                logger.warning(f"LLM evaluation failed on attempt {attempt}: {str(e)}")

        logger.warning("All LLM attempts exhausted or invalid response. Falling back to deterministic scoring.")
        return None, "heuristic_fallback"

    @staticmethod
    def _build_user_prompt(
        candidate_data: Dict[str, Any],
        jd_requirements: Dict[str, Any],
        raw_resume_text: str,
        raw_jd_text: str
    ) -> str:
        return f"""
EVALUATE THIS CANDIDATE RESUME AGAINST THE JOB DESCRIPTION:

=== JOB DESCRIPTION ===
Title: {jd_requirements.get('title', 'Position')}
Required Skills: {', '.join(jd_requirements.get('required_skills', []))}
Preferred Skills: {', '.join(jd_requirements.get('preferred_skills', []))}
Minimum Experience: {jd_requirements.get('min_years_experience', 0)} years
Education Requirements: {', '.join(jd_requirements.get('education_requirements', []))}
Domain Focus: {', '.join(jd_requirements.get('domain_requirements', []))}

Full JD Context:
{raw_jd_text[:1500]}

=== CANDIDATE PROFILE ===
Name: {candidate_data.get('name', 'Unknown Candidate')}
Total Years Experience: {candidate_data.get('total_years_experience', 0)} years
Extracted Skills: {', '.join(candidate_data.get('technical_skills', []))}
Education: {json.dumps(candidate_data.get('education', []))}
Certifications: {', '.join(candidate_data.get('certifications', []))}

Resume Excerpt:
{raw_resume_text[:2500]}

Analyze semantically and output strict JSON according to the instructions.
"""

    @staticmethod
    def _extract_and_repair_json(content: str) -> Optional[Dict[str, Any]]:
        """Cleans markdown backticks and common formatting irregularities in LLM output."""
        if not content:
            return None

        clean = content.strip()
        # Remove ```json ... ``` code fences
        if clean.startswith("```"):
            clean = re.sub(r"^```[a-zA-Z]*\n?", "", clean)
            clean = re.sub(r"\n?```$", "", clean).strip()

        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            # Try finding first { and last }
            first_brace = clean.find("{")
            last_brace = clean.rfind("}")
            if first_brace != -1 and last_brace != -1:
                sub = clean[first_brace:last_brace + 1]
                try:
                    return json.loads(sub)
                except Exception:
                    pass
        return None
