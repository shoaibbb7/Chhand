"""API router aggregation."""

from fastapi import APIRouter

from app.api.analyze import router as analyze_router
from app.api.health import router as health_router
from app.api.rewrite import router as rewrite_router
from app.api.rhyme import router as rhyme_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(analyze_router)
api_router.include_router(rewrite_router)
api_router.include_router(rhyme_router)

__all__ = ["api_router"]
