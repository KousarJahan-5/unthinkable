import pytest
from app.services.llm_service import LLMService
from app.schemas.analysis import CandidateAnalysisOutput


def test_extract_and_repair_json_clean():
    raw_json = '{"candidate_name": "Test", "overall_score": 8.5, "recommendation": "Strong Match"}'
    parsed = LLMService._extract_and_repair_json(raw_json)
    assert parsed is not None
    assert parsed["candidate_name"] == "Test"
    assert parsed["overall_score"] == 8.5


def test_extract_and_repair_json_markdown_wrapped():
    markdown_json = '```json\n{"candidate_name": "Alex", "overall_score": 9.0, "recommendation": "Strong Match"}\n```'
    parsed = LLMService._extract_and_repair_json(markdown_json)
    assert parsed is not None
    assert parsed["candidate_name"] == "Alex"


def test_pydantic_schema_validation():
    sample_dict = {
        "candidate_name": "Sarah",
        "overall_score": 7.5,
        "recommendation": "Match",
        "skills_match": {
            "matched": ["Python", "FastAPI"],
            "partial": ["Docker"],
            "missing": ["Kubernetes"]
        },
        "experience_match": {
            "score": 8.0,
            "summary": "5 years relevant experience."
        },
        "education_match": {
            "score": 8.5,
            "summary": "B.S. in CS."
        },
        "relevant_projects": ["Microservice API"],
        "strengths": ["Strong Python skills"],
        "gaps": ["Lacks K8s"],
        "justification": "Good candidate for backend role."
    }
    validated = CandidateAnalysisOutput(**sample_dict)
    assert validated.candidate_name == "Sarah"
    assert validated.overall_score == 7.5
    assert validated.recommendation == "Match"
    assert len(validated.skills_match.matched) == 2
