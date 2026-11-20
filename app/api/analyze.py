"""Meter analysis endpoint."""

from fastapi import APIRouter

from app.meter.scanner import scan_poem
from app.meter.templates import get_template
from app.schemas import AnalyzeRequest, AnalyzeResponse

router = APIRouter(tags=["Meter"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_poem(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Deterministically calculates matra counts, syllable weights,
    break positions, and error diagnostics for a poem's charans.
    """
    template = get_template(request.meter, request.custom_pattern)
    return scan_poem(
        charans=request.charans,
        template=template,
        pronunciation_mode=request.pronunciation_mode,
        pronunciation_overrides=request.pronunciation_overrides,
    )
