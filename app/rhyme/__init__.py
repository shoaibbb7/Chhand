"""Rhyme assistant package."""

from app.rhyme.endings import are_rhymes, extract_rhyme_tail
from app.rhyme.suggester import load_rhyme_families, suggest_rhymes

__all__ = ["are_rhymes", "extract_rhyme_tail", "load_rhyme_families", "suggest_rhymes"]
