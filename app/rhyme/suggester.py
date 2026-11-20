"""Rhyme suggestion engine with dictionary lookup and optional LLM fallback."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from app.meter.normalize import normalize_devanagari
from app.rhyme.endings import extract_last_word, extract_rhyme_tail
from app.schemas import RhymeMatch, RhymeResponse

DICTIONARY_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "rhyme_words.txt"


@lru_cache(maxsize=1)
def load_rhyme_dictionary() -> list[str]:
    """Loads and normalizes the starter Hindi rhyme dictionary."""
    if not DICTIONARY_PATH.exists():
        return []
    words: list[str] = []
    seen: set[str] = set()
    with open(DICTIONARY_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            norm = normalize_devanagari(line).normalized.strip()
            if norm and norm not in seen:
                seen.add(norm)
                words.append(norm)
    return words


@lru_cache(maxsize=1)
def load_rhyme_families() -> dict[str, list[str]]:
    """Loads dictionary words grouped by authentic Devanagari rhyme ending."""
    if not DICTIONARY_PATH.exists():
        return {}
    families: dict[str, list[str]] = {}
    with open(DICTIONARY_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            norm = normalize_devanagari(line).normalized.strip()
            if norm:
                tail = extract_rhyme_tail(norm)
                group_key = f"-{tail}" if tail else "other"
                if group_key not in families:
                    families[group_key] = []
                if norm not in families[group_key]:
                    families[group_key].append(norm)
    return families


async def suggest_rhymes(
    word_or_phrase: str,
    limit: int = 10,
    llm_client: Any | None = None,
) -> RhymeResponse:
    """
    Finds exact and approximate Hindi rhyme words for the given word or line ending.
    Deterministic dictionary lookup runs offline; LLM fallback is optional and verified.
    """
    clean_target = extract_last_word(word_or_phrase)
    norm_target = normalize_devanagari(clean_target).normalized.strip()
    target_tail = extract_rhyme_tail(norm_target)

    if not target_tail:
        return RhymeResponse(
            original_word=clean_target,
            rhyme_tail="",
            exact_matches=[],
            approximate_matches=[],
            all_matches=[],
            category="unknown",
        )

    dictionary = load_rhyme_dictionary()
    exact_matches: list[str] = []
    approximate_matches: list[str] = []
    seen: set[str] = {norm_target}

    # 1. Match against deterministic local dictionary
    for entry in dictionary:
        if entry in seen:
            continue
        entry_tail = extract_rhyme_tail(entry)
        if entry_tail == target_tail:
            exact_matches.append(entry)
            seen.add(entry)
        elif len(target_tail) >= 2 and (
            entry_tail.endswith(target_tail[-1]) or target_tail.endswith(entry_tail[-1])
        ):
            approximate_matches.append(entry)
            seen.add(entry)

    # 2. Optional LLM fallback if exact matches are few and client is configured
    if len(exact_matches) < limit and llm_client and getattr(llm_client, "is_configured", False):
        try:
            from app.llm.prompts import build_rhyme_prompt

            prompt = build_rhyme_prompt(clean_target, count=limit)
            data = await llm_client.generate_json(
                [{"role": "user", "content": prompt}],
                temperature=0.5,
            )
            raw_candidates = data.get("rhymes", [])
            for cand in raw_candidates:
                cand_clean = extract_last_word(str(cand)).strip()
                cand_norm = normalize_devanagari(cand_clean).normalized
                if cand_norm and cand_norm not in seen:
                    # Strictly verify candidate ending with deterministic extractor
                    cand_tail = extract_rhyme_tail(cand_norm)
                    if cand_tail == target_tail:
                        exact_matches.append(cand_norm)
                        seen.add(cand_norm)
        except Exception:
            # Fallback gracefully to dictionary results on LLM failure
            pass

    # Build structured list
    all_matches: list[RhymeMatch] = []
    for w in exact_matches[:limit]:
        all_matches.append(
            RhymeMatch(
                word=w,
                match_type="exact",
                rhyme_tail=target_tail,
                score=1.0,
            )
        )
    remaining_limit = max(0, limit - len(all_matches))
    for w in approximate_matches[:remaining_limit]:
        all_matches.append(
            RhymeMatch(
                word=w,
                match_type="approximate",
                rhyme_tail=target_tail,
                score=0.7,
            )
        )

    return RhymeResponse(
        original_word=clean_target,
        rhyme_tail=target_tail,
        exact_matches=exact_matches[:limit],
        approximate_matches=approximate_matches[:limit],
        all_matches=all_matches,
        category=f"Endings in -{target_tail}",
    )
