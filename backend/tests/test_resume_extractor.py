import pytest
from app.services.resume_extractor import ResumeExtractor


def test_resume_extractor_full_profile(sample_strong_resume_text):
    cand = ResumeExtractor.extract(sample_strong_resume_text, "Alex_Chen_Resume.pdf")
    assert cand["name"] == "Alex Chen"
    assert cand["email"] == "alex@example.com"
    assert cand["phone"] == "+1 (415) 555-0192"
    assert "Python" in cand["technical_skills"]
    assert "FastAPI" in cand["technical_skills"]
    assert cand["total_years_experience"] == 6
    assert len(cand["education"]) >= 1


def test_resume_extractor_null_safety():
    # Empty or minimal resume should not crash or invent fields
    minimal_text = "Jane Doe\nLooking for work."
    cand = ResumeExtractor.extract(minimal_text)
    assert cand["name"] == "Jane Doe"
    assert cand["email"] is None
    assert cand["phone"] is None
    assert cand["skills"] == []
    assert cand["experience"] == []
    assert cand["education"] == []
