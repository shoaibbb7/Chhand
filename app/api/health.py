"""Health check endpoint."""

from fastapi import APIRouter

from app.config import settings
from app.schemas import HealthResponse

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Returns application health, version, and capability disclosure."""
    llm_info: dict[str, str | bool] = {
        "provider": "gemini",
        "configured": settings.is_gemini_configured,
    }
    if settings.is_gemini_configured:
        llm_info["model"] = settings.GEMINI_MODEL

    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        meter_engine={"available": True},
        llm=llm_info,
        llm_configured=settings.is_gemini_configured,
        environment=settings.ENV,
    )
