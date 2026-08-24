import re
from typing import Dict, Any, List, Optional, Tuple
from app.utils.text_cleaner import extract_emails, extract_phone_numbers, extract_urls


# Comprehensive tech skills dictionary for taxonomy extraction
KNOWN_TECH_SKILLS = {
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
    "react", "react.js", "reactjs", "next.js", "nextjs", "vue", "vue.js", "angular", "svelte", "html", "css", "tailwind", "sass",
    "fastapi", "flask", "django", "node.js", "nodejs", "express", "express.js", "spring boot", "asp.net", "nest.js",
    "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "neo4j", "sql",
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform", "ansible", "ci/cd", "git", "github actions",
    "machine learning", "ml", "deep learning", "dl", "nlp", "natural language processing", "computer vision", "cv",
    "llm", "llms", "large language models", "rag", "langchain", "llamaindex", "hugging face", "transformers", "pytorch", "tensorflow",
    "keras", "scikit-learn", "pandas", "numpy", "opencv", "spacy", "bert", "openai", "claude", "gemini",
    "graphql", "rest", "restful api", "grpc", "microservices", "kafka", "rabbitmq", "celery", "airflow",
    "agile", "scrum", "jira", "pytest", "unit testing", "tdd", "system design", "distributed systems"
}

# Certifications keywords
KNOWN_CERTS = [
    "aws certified", "solutions architect", "developer associate", "sysops administrator",
    "google cloud certified", "professional cloud architect", "professional data engineer",
    "azure certified", "azure fundamentals", "az-900", "az-104", "az-204", "az-305",
    "certified kubernetes administrator", "cka", "ckad", "cissp", "ceh", "comptia security+",
    "pmp", "project management professional", "scrum master", "csm", "psm", "hashicorp certified terraform"
]


class ResumeExtractor:
    """Extracts structured candidate information deterministically from raw resume text."""

    @classmethod
    def extract(cls, raw_text: str, filename: Optional[str] = None) -> Dict[str, Any]:
        if not raw_text:
            return cls._empty_candidate()

        email = cls._extract_email(raw_text)
        phone = cls._extract_phone(raw_text)
        name = cls._extract_name(raw_text, email, filename)
        skills, tech_skills = cls._extract_skills(raw_text)
        education = cls._extract_education(raw_text)
        experience, total_years = cls._extract_experience(raw_text)
        projects = cls._extract_projects(raw_text)
        certs = cls._extract_certifications(raw_text)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "location": cls._extract_location(raw_text),
            "skills": skills,
            "technical_skills": tech_skills,
            "experience": experience,
            "total_years_experience": total_years,
            "education": education,
            "projects": projects,
            "certifications": certs,
        }

    @staticmethod
    def _empty_candidate() -> Dict[str, Any]:
        return {
            "name": "Unknown Candidate",
            "email": None,
            "phone": None,
            "location": None,
            "skills": [],
            "technical_skills": [],
            "experience": [],
            "total_years_experience": 0,
            "education": [],
            "projects": [],
            "certifications": [],
        }

    @staticmethod
    def _extract_email(text: str) -> Optional[str]:
        emails = extract_emails(text)
        return emails[0] if emails else None

    @staticmethod
    def _extract_phone(text: str) -> Optional[str]:
        phones = extract_phone_numbers(text)
        return phones[0] if phones else None

    @staticmethod
    def _extract_name(text: str, email: Optional[str] = None, filename: Optional[str] = None) -> str:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # Check first 5 lines for a candidate name
        for line in lines[:5]:
            # Skip lines that look like emails, URLs, or headers
            if "@" in line or "http" in line or "resume" in line.lower() or "curriculum" in line.lower():
                continue
            # Look for 2 to 4 words with alphabets
            words = line.split()
            if 2 <= len(words) <= 4:
                if all(re.match(r"^[A-Z][a-zA-Z\.\'-]+$", w) for w in words):
                    return line
                elif all(w.isalpha() for w in words) and len(line) < 35:
                    return line.title()

        # Fallback: extract from filename if e.g. "Alex_Chen_Resume.pdf"
        if filename:
            clean_fn = re.sub(r'[\-_]', ' ', re.sub(r'\.[^.]+$', '', filename))
            clean_fn = re.sub(r'(?i)\b(resume|cv|profile|senior|junior|lead|developer|engineer)\b', '', clean_fn).strip()
            if clean_fn and len(clean_fn.split()) in [2, 3]:
                return clean_fn.title()

        # Fallback: extract username prefix from email if available
        if email:
            prefix = email.split("@")[0]
            parts = re.split(r'[\._]', prefix)
            if len(parts) >= 2 and all(p.isalpha() for p in parts):
                return " ".join(parts).title()

        return "Unknown Candidate"

    @staticmethod
    def _extract_location(text: str) -> Optional[str]:
        # Look for City, State / Country patterns
        loc_patterns = [
            r'([A-Z][a-zA-Z\s]+,\s*(?:[A-Z]{2}|California|New York|Texas|Washington|India|Canada|UK|United States|Germany))',
            r'(Remote|Hybrid|San Francisco|New York|Seattle|Austin|Bangalore|London|Berlin|Toronto)',
        ]
        for pattern in loc_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    @classmethod
    def _extract_skills(cls, text: str) -> Tuple[List[str], List[str]]:
        found_tech: List[str] = []
        text_lower = " " + text.lower() + " "

        for skill in KNOWN_TECH_SKILLS:
            # Word boundary check
            escaped = re.escape(skill)
            pattern = rf'(?<![a-zA-Z0-9_#\+]){escaped}(?![a-zA-Z0-9_#\+])'
            if re.search(pattern, text_lower):
                # Normalize display casing
                display_name = skill.title()
                if skill in ["ml", "nlp", "cv", "rag", "k8s", "ci/cd", "tdd", "aws", "gcp", "sql"]:
                    display_name = skill.upper()
                elif skill in ["react.js", "reactjs", "react"]:
                    display_name = "React"
                elif skill in ["node.js", "nodejs"]:
                    display_name = "Node.js"
                elif skill in ["vue.js", "vue"]:
                    display_name = "Vue.js"
                elif skill in ["next.js", "nextjs"]:
                    display_name = "Next.js"
                elif skill in ["c++"]:
                    display_name = "C++"
                elif skill in ["c#"]:
                    display_name = "C#"
                elif skill in ["postgresql", "postgres"]:
                    display_name = "PostgreSQL"
                elif skill in ["fastapi"]:
                    display_name = "FastAPI"
                elif skill in ["pytorch"]:
                    display_name = "PyTorch"
                elif skill in ["tensorflow"]:
                    display_name = "TensorFlow"
                elif skill in ["scikit-learn"]:
                    display_name = "Scikit-Learn"

                if display_name not in found_tech:
                    found_tech.append(display_name)

        return found_tech, found_tech

    @staticmethod
    def _extract_education(text: str) -> List[Dict[str, Any]]:
        education_entries = []
        # Degrees
        degree_patterns = [
            (r"(?i)\b(ph\.?d|doctor of philosophy)\b", "Ph.D."),
            (r"(?i)\b(master(?:'s)? of science|m\.?s\.?|msc|m\.?tech)\b", "Master of Science (M.S.)"),
            (r"(?i)\b(master(?:'s)? of business administration|mba)\b", "MBA"),
            (r"(?i)\b(bachelor(?:'s)? of science|b\.?s\.?|bsc|b\.?tech|b\.?e\.?)\b", "Bachelor of Science (B.S.)"),
            (r"(?i)\b(bachelor(?:'s)? of arts|b\.?a\.?)\b", "Bachelor of Arts (B.A.)"),
            (r"(?i)\b(associate(?:'s)? degree)\b", "Associate Degree"),
        ]

        lines = text.split("\n")
        edu_section = False
        captured_text = []

        for i, line in enumerate(lines):
            l_lower = line.strip().lower()
            if any(h in l_lower for h in ["education", "academic background", "qualification"]):
                edu_section = True
                continue
            if edu_section and any(h in l_lower for h in ["experience", "employment", "projects", "skills", "certifications"]):
                break
            if edu_section:
                captured_text.append(line)

        target_text = "\n".join(captured_text) if captured_text else text

        for pattern, standard_degree in degree_patterns:
            match = re.search(pattern, target_text)
            if match:
                # Find university context
                uni_match = re.search(r"(?i)(?:at|from|,\s*)?([A-Z][a-zA-Z\s]+(?:University|College|Institute|Polytechnic|Academy))", target_text)
                institution = uni_match.group(1).strip() if uni_match else "Recognized University"
                
                # Year match
                year_match = re.search(r"\b(20[0-2][0-9]|19[89][0-9])\b", target_text)
                year = year_match.group(1) if year_match else None

                # Field of study
                field_match = re.search(r"(?i)(?:in|of)\s+(Computer Science|Software Engineering|Data Science|Electrical Engineering|Information Technology|Mathematics|Artificial Intelligence)", target_text)
                field = field_match.group(1) if field_match else "Computer Science / Related Field"

                education_entries.append({
                    "degree": f"{standard_degree} in {field}",
                    "institution": institution,
                    "year": year,
                    "field_of_study": field
                })
                break

        return education_entries

    @staticmethod
    def _extract_experience(text: str) -> Tuple[List[Dict[str, Any]], int]:
        experience_entries = []
        total_years = 0

        # Look for explicit years mentioned like "5+ years of experience", "6 years experience"
        exp_mention = re.search(r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience', text, re.IGNORECASE)
        if exp_mention:
            total_years = int(exp_mention.group(1))

        # Parse job roles from experience section
        lines = text.split("\n")
        exp_section = False
        current_role = None

        role_patterns = [
            r'(?i)\b(Senior|Lead|Principal|Staff|Junior|Mid-level)?\s*(Software Engineer|Full Stack Developer|Frontend Engineer|Backend Developer|Machine Learning Engineer|AI Engineer|Data Scientist|DevOps Engineer|System Architect|Data Analyst|Product Manager)\b',
        ]

        for line in lines:
            l_lower = line.strip().lower()
            if any(h in l_lower for h in ["work experience", "professional experience", "employment history", "experience:"]):
                exp_section = True
                continue
            if exp_section and any(h in l_lower for h in ["education", "skills", "projects", "certifications", "interests"]):
                break

            if exp_section:
                for pat in role_patterns:
                    m = re.search(pat, line)
                    if m:
                        title = m.group(0).strip()
                        # Extract date range if present e.g. 2020 - Present, 2019 - 2023
                        date_match = re.search(r'((?:20\d\d|19\d\d|Present|Current)\s*[-–—]\s*(?:20\d\d|Present|Current))', line, re.IGNORECASE)
                        duration = date_match.group(1) if date_match else "Recent"
                        experience_entries.append({
                            "title": title,
                            "company": "Tech Company",
                            "duration": duration,
                            "description": line
                        })
                        break

        # Fallback years calculation if not explicitly stated
        if total_years == 0 and experience_entries:
            total_years = min(15, max(1, len(experience_entries) * 2))

        return experience_entries, total_years

    @staticmethod
    def _extract_projects(text: str) -> List[Dict[str, Any]]:
        projects = []
        lines = text.split("\n")
        proj_section = False

        for line in lines:
            l_lower = line.strip().lower()
            if any(h in l_lower for h in ["projects", "personal projects", "key projects", "notable projects"]):
                proj_section = True
                continue
            if proj_section and any(h in l_lower for h in ["education", "skills", "certifications", "work experience", "awards"]):
                break

            if proj_section and line.strip().startswith("-") or (proj_section and ":" in line and len(line) < 100):
                parts = line.split(":", 1)
                name = parts[0].lstrip("- *#").strip()
                desc = parts[1].strip() if len(parts) > 1 else line.strip()
                if len(name) > 3 and not any(k in name.lower() for k in ["skills", "education", "experience"]):
                    projects.append({
                        "name": name,
                        "description": desc,
                        "technologies": [s for s in KNOWN_TECH_SKILLS if s in line.lower()]
                    })

        return projects[:5]

    @staticmethod
    def _extract_certifications(text: str) -> List[str]:
        certs = []
        text_lower = text.lower()
        for cert in KNOWN_CERTS:
            if cert in text_lower:
                certs.append(cert.title())
        return list(dict.fromkeys(certs))
