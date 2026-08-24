import pytest
from app.services.scoring_engine import ScoringEngine, are_skills_equivalent


def test_semantic_equivalence():
    assert are_skills_equivalent("ML", "Machine Learning")
    assert are_skills_equivalent("NLP", "Natural Language Processing")
    assert are_skills_equivalent("PostgreSQL", "SQL database experience")
    assert are_skills_equivalent("k8s", "Kubernetes")
    # Unrelated skills should not match
    assert not are_skills_equivalent("Python", "Photoshop")
    assert not are_skills_equivalent("React", "Kubernetes")


def test_scoring_engine_strong_candidate():
    candidate_data = {
        "name": "Alex Chen",
        "total_years_experience": 6,
        "technical_skills": ["Python", "FastAPI", "PostgreSQL", "LLM", "RAG", "PyTorch", "Docker", "Kubernetes", "React"],
        "education": [{"degree": "Master of Science in Computer Science", "institution": "Stanford University"}],
        "projects": [{"name": "AI Pipeline", "description": "Built RAG LLM engine", "technologies": ["Python", "FastAPI"]}],
        "certifications": ["AWS Certified Solutions Architect"]
    }
    jd_requirements = {
        "title": "Senior AI Engineer",
        "min_years_experience": 5,
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "LLM", "RAG", "PyTorch"],
        "preferred_skills": ["Kubernetes", "React"],
        "education_requirements": ["Master's or Bachelor's in Computer Science"]
    }

    result = ScoringEngine.calculate_score(candidate_data, jd_requirements)
    assert result.overall_score >= 8.0
    assert result.recommendation == "Strong Match"
    assert len(result.skills_match.missing) == 0
    assert len(result.strengths) >= 1


def test_scoring_engine_weak_candidate():
    candidate_data = {
        "name": "Graphic Designer",
        "total_years_experience": 1,
        "technical_skills": ["Photoshop", "Illustrator", "Figma"],
        "education": [{"degree": "Bachelor of Fine Arts", "institution": "Art Institute"}],
        "projects": [],
        "certifications": []
    }
    jd_requirements = {
        "title": "Senior AI Engineer",
        "min_years_experience": 5,
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "LLM", "PyTorch"],
        "preferred_skills": ["Kubernetes"],
        "education_requirements": ["Bachelor's in Computer Science"]
    }

    result = ScoringEngine.calculate_score(candidate_data, jd_requirements)
    assert result.overall_score < 4.5
    assert result.recommendation == "Weak Match"
    assert len(result.skills_match.missing) >= 4
    assert len(result.gaps) >= 1
