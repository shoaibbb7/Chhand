"""Meter-verified rewrite suggestions endpoint."""

from fastapi import APIRouter

from app.llm.verify_loop import generate_verified_suggestions
from app.schemas import RewriteRequest, RewriteResponse

router = APIRouter(tags=["AI Assist"])


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_line(request: RewriteRequest) -> RewriteResponse:
    """
    Generates AI rewrite candidates and runs every candidate through
    the deterministic Python meter engine. Returns ONLY verified matches.
    """
    return await generate_verified_suggestions(request)
