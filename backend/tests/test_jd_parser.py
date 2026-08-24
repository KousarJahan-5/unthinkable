import pytest
from app.services.jd_parser import JDParser


def test_jd_parser_structured_requirements(sample_jd_text):
    parsed = JDParser.parse(sample_jd_text, "Senior AI Engineer")
    assert parsed["title"] == "Senior AI Engineer"
    assert parsed["min_years_experience"] == 5
    assert "Python" in parsed["required_skills"]
    assert "FastAPI" in parsed["required_skills"]
    assert "Kubernetes" in parsed["preferred_skills"] or "React" in parsed["preferred_skills"]
    assert len(parsed["education_requirements"]) > 0


def test_jd_parser_empty_text():
    parsed = JDParser.parse("", "Default Job")
    assert parsed["title"] == "Default Job"
    assert parsed["required_skills"] == []
    assert parsed["min_years_experience"] == 0
