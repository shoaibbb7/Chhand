"""Laghu and Guru weight assignment for Devanagari syllables."""

from app.meter.syllables import Syllable
from app.schemas import SyllableDetail


def assign_weights(
    syllables: list[Syllable],
    pronunciation_overrides: dict[str, int] | None = None,
) -> list[SyllableDetail]:
    """
    Assigns Laghu (1) or Guru (2) weights to a sequence of syllables
    following classical Hindi Pingala Chhand Shastra.
    """
    overrides = pronunciation_overrides or {}
    results: list[SyllableDetail] = []
    running_cumulative = 0

    for idx, s in enumerate(syllables):
        w: int
        reason: str

        # 1. Check if user provided an explicit override by text or index
        if str(idx) in overrides:
            w = overrides[str(idx)]
            reason = "manual_override"
        elif s.text in overrides:
            w = overrides[s.text]
            reason = "manual_override"
        # 2. Long Vowel (दीर्घ स्वर / दीर्घ मात्रा) -> Always Guru (2)
        elif s.vowel_type == "long":
            w = 2
            reason = "long_vowel"
        # 3. Anusvara (अनुस्वार) on short vowel -> Guru (2)
        elif s.has_anusvara:
            w = 2
            reason = "anusvara_closed"
        # 4. Visarga (विसर्ग) on short vowel -> Guru (2)
        elif s.has_visarga:
            w = 2
            reason = "visarga_closed"
        # 5. Closed by a coda consonant (हलन्त युक्त वर्ण) -> Guru (2)
        elif s.is_isolated_coda:
            w = 2
            reason = "coda_closed"
        # 6. Precedes a consonant cluster in the same word (संयोगे गुरु) -> Guru (2)
        elif s.precedes_cluster:
            w = 2
            reason = "preceding_conjunct"
        # 7. Short vowel with Chandrabindu (अनुनासिक) -> Remains Laghu (1)
        elif s.has_chandrabindu:
            w = 1
            reason = "short_vowel_chandrabindu"
        # 8. Regular Short Vowel or Inherent 'a' -> Laghu (1)
        else:
            w = 1
            reason = "inherent_vowel" if s.vowel_type == "inherent" else "short_vowel"

        running_cumulative += w
        results.append(
            SyllableDetail(
                text=s.text,
                weight=w,
                classification="guru" if w >= 2 else "laghu",
                start=s.orig_start,
                end=s.orig_end,
                reason=reason,
                cumulative=running_cumulative,
            )
        )

    return results
