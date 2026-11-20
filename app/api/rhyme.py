"""Rhyme assistance endpoint."""

from typing import Any

from fastapi import APIRouter

from app.llm.client import LLMClient
from app.rhyme.suggester import load_rhyme_families, suggest_rhymes
from app.schemas import RhymeRequest, RhymeResponse

router = APIRouter(tags=["Rhyme"])


@router.get("/rhyme/families")
async def get_rhyme_families() -> dict[str, Any]:
    """Returns grouped rhyme ending families backed by the local dictionary."""
    families = load_rhyme_families()
    return {
        "families": [
            {
                "ending": k,
                "words": v,
                "sample": v[:5],
                "count": len(v),
            }
            for k, v in families.items()
        ]
    }


@router.post("/rhyme", response_model=RhymeResponse)
async def get_rhymes(request: RhymeRequest) -> RhymeResponse:
    """
    Finds compatible Hindi rhyming words using local phonetic dictionary,
    with optional verified LLM candidate fallback.
    """
    llm = LLMClient()
    return await suggest_rhymes(
        word_or_phrase=request.word,
        limit=request.limit,
        llm_client=llm if llm.is_configured else None,
    )
