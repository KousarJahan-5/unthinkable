from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/api/health")
def health_check():
    """System health check & LLM integration status."""
    has_api_key = bool(settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 5)
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "llm_provider": "OpenAI-Compatible",
        "llm_configured": has_api_key,
        "llm_model": settings.OPENAI_MODEL if has_api_key else "High-Fidelity Heuristic Fallback Engine",
        "evaluation_mode": "LLM (OpenAI API)" if has_api_key else "Deterministic Semantic Engine (Zero-setup)"
    }
