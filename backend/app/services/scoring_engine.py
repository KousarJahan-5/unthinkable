import re
from typing import Dict, Any, List, Set, Tuple, Optional
from app.schemas.analysis import CandidateAnalysisOutput, SkillsMatchSchema, SubMatchScore

# Semantic Equivalence Mapping for skills
SEMANTIC_EQUIVALENTS: Dict[str, Set[str]] = {
    "ml": {"machine learning", "statistical modeling", "predictive modeling"},
    "machine learning": {"ml", "statistical modeling", "deep learning", "ai"},
    "nlp": {"natural language processing", "text mining", "computational linguistics", "llm", "large language models"},
    "natural language processing": {"nlp", "llm", "text mining", "transformers"},
    "llm": {"large language models", "generative ai", "nlp", "rag", "gpt", "transformers"},
    "large language models": {"llm", "generative ai", "nlp", "rag"},
    "rag": {"retrieval augmented generation", "vector search", "llm", "embeddings"},
    "postgresql": {"postgres", "sql database experience", "relational database", "rdbms", "sql"},
    "sql": {"postgresql", "mysql", "sqlite", "relational database", "rdbms"},
    "react": {"reactjs", "react.js", "frontend development", "spa", "javascript", "typescript"},
    "fastapi": {"python backend", "rest api", "python restful", "async python"},
    "django": {"python backend", "python web framework"},
    "docker": {"containerization", "containers", "devops"},
    "kubernetes": {"k8s", "container orchestration", "cloud native"},
    "k8s": {"kubernetes", "container orchestration"},
    "aws": {"amazon web services", "cloud infrastructure", "cloud computing"},
    "gcp": {"google cloud", "google cloud platform", "cloud computing"},
    "azure": {"microsoft azure", "cloud computing"},
    "ci/cd": {"continuous integration", "github actions", "gitlab ci", "jenkins"},
    "tdd": {"test driven development", "unit testing", "pytest", "automated testing"},
    "rest": {"restful api", "web api", "http api"},
    "microservices": {"distributed systems", "service-oriented architecture"}
}


def are_skills_equivalent(skill_a: str, skill_b: str) -> bool:
    """Check if two skill terms are semantically equivalent."""
    a = skill_a.lower().strip()
    b = skill_b.lower().strip()
    
    if a == b:
        return True
    
    # Direct substring / containment check for exact roots
    if len(a) > 3 and len(b) > 3 and (a in b or b in a):
        return True
        
    # Check semantic lookup table
    if a in SEMANTIC_EQUIVALENTS and b in SEMANTIC_EQUIVALENTS[a]:
        return True
    if b in SEMANTIC_EQUIVALENTS and a in SEMANTIC_EQUIVALENTS[b]:
        return True
        
    return False


class ScoringEngine:
    """
    Transparent weighted scoring engine:
    - Skills match: 40% (Required 30%, Preferred 10%)
    - Relevant experience: 30% (Years & Role match)
    - Education: 10% (Degree level & STEM relevance)
    - Projects/domain relevance: 10% (Domain practical projects)
    - Other JD requirements: 10% (Certifications, soft skills, location)
    Normalized score: 1.0 to 10.0
    """

    @classmethod
    def calculate_score(
        cls,
        candidate_data: Dict[str, Any],
        jd_requirements: Dict[str, Any],
        llm_analysis: Optional[CandidateAnalysisOutput] = None
    ) -> CandidateAnalysisOutput:
        """
        Calculates and validates the overall score, blending LLM semantic insights
        with strict backend formula normalization.
        """
        # 1. Skills Assessment (40%)
        skills_match, skills_subscore = cls._evaluate_skills(
            candidate_skills=candidate_data.get("technical_skills", []) or candidate_data.get("skills", []),
            required_skills=jd_requirements.get("required_skills", []),
            preferred_skills=jd_requirements.get("preferred_skills", []),
            llm_skills=llm_analysis.skills_match if llm_analysis else None
        )

        # 2. Experience Assessment (30%)
        exp_subscore, exp_summary = cls._evaluate_experience(
            candidate_years=candidate_data.get("total_years_experience", 0),
            candidate_exp_entries=candidate_data.get("experience", []),
            required_min_years=jd_requirements.get("min_years_experience", 0),
            jd_title=jd_requirements.get("title", "Software Engineer"),
            llm_exp=llm_analysis.experience_match if llm_analysis else None
        )

        # 3. Education Assessment (10%)
        edu_subscore, edu_summary = cls._evaluate_education(
            candidate_edu=candidate_data.get("education", []),
            required_edu=jd_requirements.get("education_requirements", []),
            llm_edu=llm_analysis.education_match if llm_analysis else None
        )

        # 4. Projects & Domain Relevance (10%)
        proj_subscore, relevant_projects = cls._evaluate_projects(
            candidate_projects=candidate_data.get("projects", []),
            domain_reqs=jd_requirements.get("domain_requirements", []),
            llm_projects=llm_analysis.relevant_projects if llm_analysis else None
        )

        # 5. Other JD Requirements (10%)
        other_subscore = cls._evaluate_other(
            candidate_certs=candidate_data.get("certifications", []),
            candidate_location=candidate_data.get("location"),
            jd_location=jd_requirements.get("location_requirements")
        )

        # Weighted calculation
        # 40% skills + 30% exp + 10% edu + 10% projects + 10% other
        weighted_score = (
            (skills_subscore * 0.40) +
            (exp_subscore * 0.30) +
            (edu_subscore * 0.10) +
            (proj_subscore * 0.10) +
            (other_subscore * 0.10)
        )

        # Clamp between 1.0 and 10.0 and round to 1 decimal
        final_score = round(max(1.0, min(10.0, weighted_score)), 1)

        # Recommendation determination
        if final_score >= 8.0:
            recommendation = "Strong Match"
        elif final_score >= 6.5:
            recommendation = "Match"
        elif final_score >= 4.5:
            recommendation = "Partial Match"
        else:
            recommendation = "Weak Match"

        # Synthesize Strengths & Gaps
        strengths, gaps = cls._generate_strengths_and_gaps(
            skills_match=skills_match,
            candidate_data=candidate_data,
            jd_requirements=jd_requirements,
            exp_subscore=exp_subscore,
            edu_subscore=edu_subscore,
            llm_analysis=llm_analysis
        )

        # Generate concise justification
        justification = cls._generate_justification(
            candidate_name=candidate_data.get("name", "Candidate"),
            final_score=final_score,
            recommendation=recommendation,
            strengths=strengths,
            gaps=gaps,
            llm_justification=llm_analysis.justification if llm_analysis else None
        )

        return CandidateAnalysisOutput(
            candidate_name=candidate_data.get("name", "Candidate"),
            overall_score=final_score,
            recommendation=recommendation,
            skills_match=skills_match,
            experience_match=SubMatchScore(score=round(exp_subscore, 1), summary=exp_summary),
            education_match=SubMatchScore(score=round(edu_subscore, 1), summary=edu_summary),
            relevant_projects=relevant_projects,
            strengths=strengths,
            gaps=gaps,
            justification=justification
        )

    @classmethod
    def _evaluate_skills(
        cls,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str],
        llm_skills: Optional[SkillsMatchSchema] = None
    ) -> Tuple[SkillsMatchSchema, float]:
        matched_set: Set[str] = set()
        partial_set: Set[str] = set()
        missing_set: Set[str] = set()

        all_target = required_skills + preferred_skills
        if not all_target:
            # If JD has no specified skills, reward candidate skills directly
            return SkillsMatchSchema(matched=candidate_skills[:8], partial=[], missing=[]), 7.5

        # Check required skills
        req_matched_count = 0
        for req in required_skills:
            found = False
            for c_skill in candidate_skills:
                if are_skills_equivalent(req, c_skill):
                    matched_set.add(c_skill)
                    req_matched_count += 1
                    found = True
                    break
            if not found:
                missing_set.add(req)

        # Check preferred skills
        pref_matched_count = 0
        for pref in preferred_skills:
            found = False
            for c_skill in candidate_skills:
                if are_skills_equivalent(pref, c_skill):
                    matched_set.add(c_skill)
                    pref_matched_count += 1
                    found = True
                    break
            if not found:
                # Preferred missing is partial gap
                partial_set.add(pref)

        # Check if LLM found additional semantic nuances
        if llm_skills:
            for s in llm_skills.matched:
                if s not in missing_set:
                    matched_set.add(s)
            for s in llm_skills.partial:
                partial_set.add(s)

        # Scoring math: Required skills 30pts (out of 40), Preferred 10pts (out of 40)
        req_ratio = req_matched_count / max(1, len(required_skills)) if required_skills else 1.0
        pref_ratio = pref_matched_count / max(1, len(preferred_skills)) if preferred_skills else 1.0

        # Subscore on a 0-10 scale
        skills_score = (req_ratio * 7.5) + (pref_ratio * 2.5)
        # Ensure non-zero if candidate has some skills
        if candidate_skills and skills_score < 2.0:
            skills_score = 2.0

        return SkillsMatchSchema(
            matched=list(matched_set),
            partial=list(partial_set),
            missing=list(missing_set)
        ), min(10.0, max(1.0, skills_score))

    @staticmethod
    def _evaluate_experience(
        candidate_years: int,
        candidate_exp_entries: List[Dict[str, Any]],
        required_min_years: int,
        jd_title: str,
        llm_exp: Optional[SubMatchScore] = None
    ) -> Tuple[float, str]:
        if required_min_years == 0:
            score = 8.5 if candidate_years >= 1 else 6.5
        elif candidate_years >= required_min_years:
            score = min(10.0, 8.0 + min(2.0, (candidate_years - required_min_years) * 0.5))
        elif candidate_years > 0:
            score = max(2.0, (candidate_years / required_min_years) * 7.0)
        else:
            score = 2.0

        # Title keyword match
        title_keywords = [w.lower() for w in jd_title.split() if len(w) > 3]
        matching_roles = []
        for entry in candidate_exp_entries:
            role = entry.get("title", "")
            if any(kw in role.lower() for kw in title_keywords):
                matching_roles.append(role)

        if matching_roles:
            score = min(10.0, score + 1.0)
            summary = f"Candidate has {candidate_years} years of relevant experience in closely aligned roles ({', '.join(matching_roles[:2])})."
        elif candidate_years > 0:
            summary = f"Candidate possesses {candidate_years} years of general software experience (Required: {required_min_years}+ years)."
        else:
            summary = "Candidate does not explicitly list professional work experience duration."

        if llm_exp and llm_exp.summary:
            summary = llm_exp.summary

        return score, summary

    @staticmethod
    def _evaluate_education(
        candidate_edu: List[Dict[str, Any]],
        required_edu: List[str],
        llm_edu: Optional[SubMatchScore] = None
    ) -> Tuple[float, str]:
        if not candidate_edu:
            return 4.0, "No formal education degrees explicitly listed on the resume."

        top_edu = candidate_edu[0]
        deg = top_edu.get("degree", "").lower()
        inst = top_edu.get("institution", "University")

        if "ph.d" in deg or "doctor" in deg:
            score = 10.0
            summary = f"Holds advanced doctorate degree: {top_edu.get('degree')} from {inst}."
        elif "master" in deg or "m.s" in deg:
            score = 9.5
            summary = f"Holds Master's degree: {top_edu.get('degree')} from {inst}."
        elif "bachelor" in deg or "b.s" in deg or "b.tech" in deg:
            score = 8.5
            summary = f"Holds Bachelor's degree: {top_edu.get('degree')} from {inst}."
        else:
            score = 6.0
            summary = f"Holds educational qualification: {top_edu.get('degree', 'Degree')}."

        if llm_edu and llm_edu.summary:
            summary = llm_edu.summary

        return score, summary

    @staticmethod
    def _evaluate_projects(
        candidate_projects: List[Dict[str, Any]],
        domain_reqs: List[str],
        llm_projects: Optional[List[Any]] = None
    ) -> Tuple[float, List[Any]]:
        if not candidate_projects:
            return 5.0, []

        relevant = []
        for p in candidate_projects:
            p_name = p.get("name", "Project")
            p_desc = p.get("description", "")
            p_tech = p.get("technologies", [])
            relevant.append(f"{p_name}: {p_desc[:120]} (Tech: {', '.join(p_tech[:4]) if p_tech else 'General'})")

        score = min(10.0, 6.0 + len(relevant) * 1.5)
        return score, relevant[:4]

    @staticmethod
    def _evaluate_other(
        candidate_certs: List[str],
        candidate_location: Optional[str],
        jd_location: Optional[str]
    ) -> float:
        score = 7.0
        if candidate_certs:
            score = min(10.0, score + len(candidate_certs) * 1.0)
        if candidate_location and jd_location and (candidate_location.lower() == "remote" or jd_location.lower() == "remote"):
            score = min(10.0, score + 1.0)
        return min(10.0, score)

    @classmethod
    def _generate_strengths_and_gaps(
        cls,
        skills_match: SkillsMatchSchema,
        candidate_data: Dict[str, Any],
        jd_requirements: Dict[str, Any],
        exp_subscore: float,
        edu_subscore: float,
        llm_analysis: Optional[CandidateAnalysisOutput] = None
    ) -> Tuple[List[str], List[str]]:
        strengths: List[str] = []
        gaps: List[str] = []

        if llm_analysis and llm_analysis.strengths:
            strengths = llm_analysis.strengths
        else:
            if skills_match.matched:
                strengths.append(f"Demonstrates core proficiency in {', '.join(skills_match.matched[:4])}.")
            if exp_subscore >= 8.0:
                strengths.append(f"Solid track record with {candidate_data.get('total_years_experience', 0)}+ years of experience matching job seniority.")
            if edu_subscore >= 8.5 and candidate_data.get("education"):
                strengths.append(f"Strong academic background: {candidate_data['education'][0].get('degree', 'Technical Degree')}.")
            if candidate_data.get("projects"):
                strengths.append(f"Practical hands-on portfolio with {len(candidate_data['projects'])} demonstrated project(s).")

        if llm_analysis and llm_analysis.gaps:
            gaps = llm_analysis.gaps
        else:
            if skills_match.missing:
                gaps.append(f"Missing required tech stack requirements: {', '.join(skills_match.missing[:3])}.")
            if exp_subscore < 6.0:
                req_y = jd_requirements.get("min_years_experience", 0)
                gaps.append(f"Years of experience ({candidate_data.get('total_years_experience', 0)} yrs) falls below target ({req_y}+ yrs).")
            if not candidate_data.get("education"):
                gaps.append("Resume does not list verified formal degree credentials.")
            if skills_match.partial:
                gaps.append(f"Partial/unverified proficiency in: {', '.join(skills_match.partial[:2])}.")

        if not strengths:
            strengths.append("Foundational technical background.")
        if not gaps:
            gaps.append("No major disqualifying gaps identified.")

        return strengths[:5], gaps[:5]

    @staticmethod
    def _generate_justification(
        candidate_name: str,
        final_score: float,
        recommendation: str,
        strengths: List[str],
        gaps: List[str],
        llm_justification: Optional[str] = None
    ) -> str:
        if llm_justification and len(llm_justification.strip()) > 30:
            return llm_justification.strip()

        strength_txt = strengths[0] if strengths else "Matches core qualifications"
        gap_txt = gaps[0] if gaps else "Meets requirements"

        return (
            f"{candidate_name} is evaluated as a **{recommendation}** (Score: {final_score}/10). "
            f"Key strength: {strength_txt} "
            f"Primary consideration: {gap_txt}"
        )
