"""Phonetic rhyme tail extraction for Hindi Devanagari words."""

import re

from app.meter.devanagari import (
    ALL_INDEPENDENT_VOWELS,
    ALL_MATRAS,
    CONSONANTS,
    is_danda,
)
from app.meter.normalize import normalize_devanagari


def extract_last_word(text: str) -> str:
    """Extracts the final word from a line or phrase."""
    cleaned = re.sub(r"[।॥|,.!?;:\"\'\-]", " ", text or "")
    words = cleaned.strip().split()
    return words[-1] if words else ""


def extract_rhyme_tail(word: str) -> str:
    """
    Extracts the normalized phonological ending sound (tuka / तुक) of a Hindi word.
    Example: 'दूर' -> 'ूर', 'नूर' -> 'ूर', 'प्यार' -> 'ार', 'जले' -> 'े'
    """
    last_word = extract_last_word(word)
    if not last_word:
        return ""

    norm = normalize_devanagari(last_word).normalized
    chars = [c for c in norm if not is_danda(c) and not c.isspace()]
    if not chars:
        return ""

    # Scan backwards to locate the last vowel nucleus (matra or independent vowel)
    vowel_idx = -1
    for i in range(len(chars) - 1, -1, -1):
        ch = chars[i]
        if ch in ALL_MATRAS or ch in ALL_INDEPENDENT_VOWELS:
            vowel_idx = i
            break

    if vowel_idx != -1:
        # Include from the vowel to the end of the word
        # e.g., for 'नूर' (न, ू, र), vowel is at index 1 -> 'ूर'
        # for 'जले' (ज, ल, े), vowel is at index 2 -> 'े'
        tail = "".join(chars[vowel_idx:])
        return tail

    # If no explicit matra found, word ends in inherent vowel + consonant (e.g. सच, मन)
    # Take the last consonant and optional trailing halant/nukta
    for i in range(len(chars) - 1, -1, -1):
        if chars[i] in CONSONANTS:
            return "".join(chars[i:])

    return "".join(chars[-2:]) if len(chars) >= 2 else "".join(chars)


def are_rhymes(word_a: str, word_b: str) -> bool:
    """Checks whether two words share a matching phonetic rhyme tail."""
    tail_a = extract_rhyme_tail(word_a)
    tail_b = extract_rhyme_tail(word_b)
    if not tail_a or not tail_b:
        return False
    return tail_a == tail_b
