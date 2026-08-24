import re
from typing import Dict, Any, List, Optional, Tuple
from app.services.resume_extractor import KNOWN_TECH_SKILLS


class JDParser:
    """Parses raw Job Description into structured requirements differentiating REQUIRED vs PREFERRED."""

    @classmethod
    def parse(cls, jd_text: str, default_title: Optional[str] = None) -> Dict[str, Any]:
        if not jd_text:
            return cls._empty_requirements(default_title)

        title = cls._extract_title(jd_text, default_title)
        min_years = cls._extract_min_years(jd_text)
        required_skills, preferred_skills = cls._extract_skills(jd_text)
        education = cls._extract_education_requirements(jd_text)
        responsibilities = cls._extract_responsibilities(jd_text)
        domain = cls._extract_domain(jd_text)
        location = cls._extract_location(jd_text)

        return {
            "title": title,
            "min_years_experience": min_years,
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "education_requirements": education,
            "responsibilities": responsibilities,
            "domain_requirements": domain,
            "location_requirements": location,
        }

    @staticmethod
    def _empty_requirements(default_title: Optional[str] = None) -> Dict[str, Any]:
        return {
            "title": default_title or "Software Position",
            "min_years_experience": 0,
            "required_skills": [],
            "preferred_skills": [],
            "education_requirements": [],
            "responsibilities": [],
            "domain_requirements": [],
            "location_requirements": "Flexible / Not Specified",
        }

    @staticmethod
    def _extract_title(text: str, default_title: Optional[str] = None) -> str:
        if default_title and len(default_title.strip()) > 3:
            return default_title.strip()

        # Check the first 3 lines
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines[:3]:
            # If line is short and looks like a job title
            if len(line) < 60 and not line.endswith(".") and any(
                w in line.lower() for w in ["engineer", "developer", "architect", "scientist", "manager", "lead", "specialist", "analyst"]
            ):
                return line

        return "Software Engineer"

    @staticmethod
    def _extract_min_years(text: str) -> int:
        patterns = [
            r'(\d+)\+?\s*(?:-\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:relevant\s+)?experience',
            r'(?:minimum|at\s+least)\s+(\d+)\s*(?:years?|yrs?)',
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
        return 0

    @classmethod
    def _extract_skills(cls, text: str) -> Tuple[List[str], List[str]]:
        """Separate required skills from preferred/nice-to-have skills."""
        lines = text.split("\n")
        
        required_section_lines = []
        preferred_section_lines = []
        general_lines = []

        current_section = "general"

        for line in lines:
            l_lower = line.strip().lower()
            if any(h in l_lower for h in ["preferred", "nice to have", "good to have", "bonus", "plus if you have", "desired qualification"]):
                current_section = "preferred"
                continue
            elif any(h in l_lower for h in ["required", "minimum qualification", "what you need", "requirements", "must have", "qualifications:"]):
                current_section = "required"
                continue
            elif any(h in l_lower for h in ["responsibilities", "about us", "benefits", "what you will do"]):
                current_section = "other"
                continue

            if current_section == "required":
                required_section_lines.append(line)
            elif current_section == "preferred":
                preferred_section_lines.append(line)
            elif current_section == "general":
                general_lines.append(line)

        req_text = " " + " ".join(required_section_lines).lower() + " "
        pref_text = " " + " ".join(preferred_section_lines).lower() + " "
        gen_text = " " + " ".join(general_lines).lower() + " "

        required_skills: List[str] = []
        preferred_skills: List[str] = []

        for skill in KNOWN_TECH_SKILLS:
            escaped = re.escape(skill)
            pattern = rf'(?<![a-zA-Z0-9_#\+]){escaped}(?![a-zA-Z0-9_#\+])'

            display = skill.title()
            if skill in ["ml", "nlp", "cv", "rag", "k8s", "ci/cd", "tdd", "aws", "gcp", "sql"]:
                display = skill.upper()
            elif skill in ["react.js", "reactjs", "react"]:
                display = "React"
            elif skill in ["node.js", "nodejs"]:
                display = "Node.js"
            elif skill in ["postgresql", "postgres"]:
                display = "PostgreSQL"
            elif skill in ["fastapi"]:
                display = "FastAPI"
            elif skill in ["pytorch"]:
                display = "PyTorch"

            if re.search(pattern, pref_text):
                if display not in preferred_skills:
                    preferred_skills.append(display)
            elif re.search(pattern, req_text):
                if display not in required_skills:
                    required_skills.append(display)
            elif re.search(pattern, gen_text):
                if display not in required_skills and display not in preferred_skills:
                    required_skills.append(display)

        # Ensure we have at least standard minimums if found
        return required_skills, preferred_skills

    @staticmethod
    def _extract_education_requirements(text: str) -> List[str]:
        edu_reqs = []
        if re.search(r'(?i)\b(bachelor|b\.?s\.?|b\.?tech|b\.?e\.?)\b', text):
            edu_reqs.append("Bachelor's degree in Computer Science or related STEM field")
        if re.search(r'(?i)\b(master|m\.?s\.?|m\.?tech)\b', text):
            edu_reqs.append("Master's degree preferred or equivalent experience")
        if re.search(r'(?i)\b(ph\.?d)\b', text):
            edu_reqs.append("Ph.D. in AI/Machine Learning/Computer Science preferred")
        return edu_reqs or ["Degree in Computer Science or equivalent practical experience"]

    @staticmethod
    def _extract_responsibilities(text: str) -> List[str]:
        responsibilities = []
        lines = text.split("\n")
        in_resp = False

        for line in lines:
            l_lower = line.strip().lower()
            if any(h in l_lower for h in ["responsibilities", "what you will do", "what you'll do", "day to day", "the role"]):
                in_resp = True
                continue
            if in_resp and any(h in l_lower for h in ["requirements", "qualifications", "preferred", "benefits", "about you"]):
                break

            if in_resp and (line.strip().startswith("-") or line.strip().startswith("*")):
                clean_item = line.lstrip("- *").strip()
                if len(clean_item) > 10:
                    responsibilities.append(clean_item)

        return responsibilities[:6]

    @staticmethod
    def _extract_domain(text: str) -> List[str]:
        domains = []
        domain_keywords = {
            "Generative AI / LLM Applications": ["generative ai", "llm", "large language models", "rag", "agents"],
            "Full Stack Web Development": ["full stack", "frontend", "backend", "web application", "spa"],
            "Cloud Infrastructure & DevOps": ["cloud native", "kubernetes", "microservices", "ci/cd", "distributed systems"],
            "Data Engineering & Analytics": ["data pipelines", "etl", "data warehouse", "analytics"],
            "FinTech / Financial Systems": ["fintech", "banking", "payments", "trading"],
            "Healthcare Tech": ["healthcare", "clinical", "biotech"],
        }
        text_lower = text.lower()
        for domain_name, keywords in domain_keywords.items():
            if any(k in text_lower for k in keywords):
                domains.append(domain_name)
        return domains or ["Software Engineering"]

    @staticmethod
    def _extract_location(text: str) -> str:
        text_lower = text.lower()
        if "remote" in text_lower:
            return "Remote"
        elif "hybrid" in text_lower:
            return "Hybrid"
        elif "on-site" in text_lower or "onsite" in text_lower:
            return "On-Site"
        return "Not Specified"
