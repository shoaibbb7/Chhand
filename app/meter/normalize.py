"""Unicode normalization with source position tracking."""

import unicodedata
from dataclasses import dataclass


@dataclass
class NormalizationResult:
    original: str
    normalized: str
    # pos_map[i] = index in original string for character normalized[i]
    pos_map: list[int]

    def map_span(self, norm_start: int, norm_end: int) -> tuple[int, int]:
        """Maps a span in normalized text [norm_start, norm_end] back to [orig_start, orig_end]."""
        if not self.normalized or norm_start >= len(self.pos_map):
            return (0, 0)
        orig_start = self.pos_map[norm_start]
        # For end, take the original end boundary
        if norm_end - 1 < len(self.pos_map):
            orig_end = self.pos_map[norm_end - 1] + 1
        else:
            orig_end = len(self.original)
        return (orig_start, max(orig_start, orig_end))


def normalize_devanagari(text: str) -> NormalizationResult:
    """
    Normalizes Devanagari text using Unicode NFC while maintaining
    a 1:1 character index map back to the original string.
    """
    if not text:
        return NormalizationResult(original="", normalized="", pos_map=[])

    # First pass: canonical decomposition / recomposition with position alignment
    # Decompose into NFD first to inspect decomposed sequences, then compose to NFC
    # But to maintain precise source coordinates, we can build character-by-character:
    original = text
    norm_chars = []
    pos_map = []

    # Replace zero-width non-joiner / joiner if purely formatting, or preserve if needed.
    # In Indic scripts, ZWJ (U+200D) and ZWNJ (U+200C) occasionally appear.
    # We normalize each character or cluster to NFC:
    for idx, char in enumerate(original):
        nfc_char = unicodedata.normalize("NFC", char)
        for c in nfc_char:
            norm_chars.append(c)
            pos_map.append(idx)

    normalized_str = "".join(norm_chars)
    # Ensure full string NFC
    full_nfc = unicodedata.normalize("NFC", normalized_str)
    if full_nfc != normalized_str:
        # Re-align if multi-char NFC recombined characters (e.g. nukta + consonant -> precomposed)
        # We can map each character in full_nfc to the corresponding original character
        pos_map = _realign_pos_map(original, full_nfc)
        normalized_str = full_nfc

    return NormalizationResult(
        original=original,
        normalized=normalized_str,
        pos_map=pos_map,
    )


def _realign_pos_map(original: str, normalized: str) -> list[int]:
    """Fallback aligner using monotonic index advancement."""
    pos_map = []
    orig_idx = 0
    orig_len = len(original)

    for _ in normalized:
        if orig_idx < orig_len:
            pos_map.append(orig_idx)
            orig_idx += 1
        else:
            pos_map.append(max(0, orig_len - 1))
    return pos_map
