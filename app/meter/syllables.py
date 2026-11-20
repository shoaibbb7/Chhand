"""Devanagari akshara segmentation and syllable extraction with source mapping."""

from dataclasses import dataclass
from typing import Literal

from app.meter.devanagari import (
    AVAGRAHA,
    is_anusvara,
    is_chandrabindu,
    is_consonant,
    is_danda,
    is_halant,
    is_independent_vowel,
    is_matra,
    is_nukta,
    is_short_matra,
    is_short_vowel,
    is_visarga,
)
from app.meter.normalize import NormalizationResult


@dataclass
class Syllable:
    """An akshara / syllabic unit extracted from Devanagari text."""

    text: str
    norm_start: int
    norm_end: int
    orig_start: int
    orig_end: int
    vowel_type: Literal["short", "long", "inherent", "none"]
    has_anusvara: bool
    has_chandrabindu: bool
    has_visarga: bool
    is_cluster_onset: bool  # Syllable starts with a consonant cluster (e.g. क्या, प्रेम)
    precedes_cluster: bool  # Next syllable in word starts with a conjunct
    word_index: int
    is_word_final: bool
    is_isolated_coda: bool = False  # e.g., consonant with halant at word end
    ambiguous: bool = False
    ambiguity_reason: str = ""


def split_syllables(
    norm_res: NormalizationResult,
    mode: Literal["orthographic", "phonetic", "manual"] = "orthographic",
) -> list[Syllable]:
    """
    Segments Devanagari text into prosodic akshara units.
    Tracks character boundaries and phonological context (e.g. following clusters).
    """
    text = norm_res.normalized
    length = len(text)
    if length == 0:
        return []

    # 1. Tokenize into words while recording character index spans
    words: list[list[tuple[int, str]]] = []
    current_word: list[tuple[int, str]] = []

    for idx, ch in enumerate(text):
        if ch.isspace() or is_danda(ch) or ch in {",", ";", ":", "-", "!", "?"}:
            if current_word:
                words.append(current_word)
                current_word = []
        else:
            current_word.append((idx, ch))
    if current_word:
        words.append(current_word)

    syllables: list[Syllable] = []

    # 2. Extract aksharas within each word
    for word_idx, word in enumerate(words):
        word_sylls = _parse_word_syllables(word, word_idx, norm_res, mode)
        # 3. Mark preceding-cluster contexts within the word
        for i in range(len(word_sylls) - 1):
            if word_sylls[i + 1].is_cluster_onset:
                word_sylls[i].precedes_cluster = True
        syllables.extend(word_sylls)

    return syllables


def _parse_word_syllables(
    word_chars: list[tuple[int, str]],
    word_idx: int,
    norm_res: NormalizationResult,
    mode: str,
) -> list[Syllable]:
    """Parses a single word into aksharas."""
    sylls: list[Syllable] = []
    w_len = len(word_chars)
    i = 0

    while i < w_len:
        start_idx, ch = word_chars[i]

        # Case 1: Avagraha (ऽ)
        if ch == AVAGRAHA:
            orig_s, orig_e = norm_res.map_span(start_idx, start_idx + 1)
            sylls.append(
                Syllable(
                    text=ch,
                    norm_start=start_idx,
                    norm_end=start_idx + 1,
                    orig_start=orig_s,
                    orig_end=orig_e,
                    vowel_type="long",
                    has_anusvara=False,
                    has_chandrabindu=False,
                    has_visarga=False,
                    is_cluster_onset=False,
                    precedes_cluster=False,
                    word_index=word_idx,
                    is_word_final=(i == w_len - 1),
                )
            )
            i += 1
            continue

        # Case 2: Independent Vowel
        if is_independent_vowel(ch):
            v_type: Literal["short", "long", "inherent", "none"] = (
                "short" if is_short_vowel(ch) else "long"
            )
            curr_norm_end = start_idx + 1
            has_anusvara = False
            has_chandrabindu = False
            has_visarga = False
            i += 1

            # Check trailing modifiers: nukta, anusvara, chandrabindu, visarga
            while i < w_len:
                nxt_idx, nxt_ch = word_chars[i]
                if is_nukta(nxt_ch):
                    curr_norm_end = nxt_idx + 1
                    i += 1
                elif is_anusvara(nxt_ch):
                    has_anusvara = True
                    curr_norm_end = nxt_idx + 1
                    i += 1
                elif is_chandrabindu(nxt_ch):
                    has_chandrabindu = True
                    curr_norm_end = nxt_idx + 1
                    i += 1
                elif is_visarga(nxt_ch):
                    has_visarga = True
                    curr_norm_end = nxt_idx + 1
                    i += 1
                else:
                    break

            surface_text = "".join(
                ch_tup[1] for ch_tup in word_chars if start_idx <= ch_tup[0] < curr_norm_end
            )
            orig_s, orig_e = norm_res.map_span(start_idx, curr_norm_end)
            is_final = i >= w_len

            sylls.append(
                Syllable(
                    text=surface_text,
                    norm_start=start_idx,
                    norm_end=curr_norm_end,
                    orig_start=orig_s,
                    orig_end=orig_e,
                    vowel_type=v_type,
                    has_anusvara=has_anusvara,
                    has_chandrabindu=has_chandrabindu,
                    has_visarga=has_visarga,
                    is_cluster_onset=False,
                    precedes_cluster=False,
                    word_index=word_idx,
                    is_word_final=is_final,
                )
            )
            continue

        # Case 3: Consonants and consonant clusters
        if is_consonant(ch):
            consonant_count = 0
            has_cluster = False
            v_type = "inherent"
            has_anusvara = False
            has_chandrabindu = False
            has_visarga = False
            has_final_halant = False

            # Collect consonant cluster: C (+ nukta)? + halant + C ...
            while i < w_len:
                c_idx, c_ch = word_chars[i]
                if is_consonant(c_ch):
                    consonant_count += 1
                    i += 1
                    # Optional nukta
                    if i < w_len and is_nukta(word_chars[i][1]):
                        i += 1
                    # Check if followed by halant
                    if i < w_len and is_halant(word_chars[i][1]):
                        # Consonant followed by halant
                        has_cluster = True
                        i += 1  # consume halant
                        # If followed by another consonant, loop continues
                        if i < w_len and is_consonant(word_chars[i][1]):
                            continue
                        else:
                            # Halant at end of cluster or word (e.g. सत्)
                            has_final_halant = True
                            v_type = "none"
                            break
                    else:
                        # Cluster ended with this consonant
                        break
                else:
                    break

            # Now check for vowel matra
            if i < w_len and is_matra(word_chars[i][1]):
                m_ch = word_chars[i][1]
                v_type = "short" if is_short_matra(m_ch) else "long"
                i += 1

            # Check for anusvara, chandrabindu, visarga
            while i < w_len:
                nxt_idx, nxt_ch = word_chars[i]
                if is_anusvara(nxt_ch):
                    has_anusvara = True
                    i += 1
                elif is_chandrabindu(nxt_ch):
                    has_chandrabindu = True
                    i += 1
                elif is_visarga(nxt_ch):
                    has_visarga = True
                    i += 1
                else:
                    break

            end_norm_idx = word_chars[i - 1][0] + 1
            surface_text = "".join(
                ch_tup[1] for ch_tup in word_chars if start_idx <= ch_tup[0] < end_norm_idx
            )
            orig_s, orig_e = norm_res.map_span(start_idx, end_norm_idx)
            is_final = i >= w_len

            # Check for trailing coda halant: e.g. "सत्"
            # If this syllable is just a consonant with halant and previous syllable exists in word,
            # it attaches as a coda to the previous syllable
            if has_final_halant and sylls:
                prev = sylls[-1]
                prev.text += surface_text
                prev.norm_end = end_norm_idx
                prev.orig_end = orig_e
                prev.is_isolated_coda = True
                prev.is_word_final = is_final
                continue

            # Schwa ambiguity handling in phonetic mode:
            ambiguous = False
            ambiguity_reason = ""
            if mode == "phonetic" and is_final and v_type == "inherent" and not has_cluster:
                ambiguous = True
                ambiguity_reason = (
                    "Final inherent schwa pronunciation may vary in modern colloquial singing."
                )

            sylls.append(
                Syllable(
                    text=surface_text,
                    norm_start=start_idx,
                    norm_end=end_norm_idx,
                    orig_start=orig_s,
                    orig_end=orig_e,
                    vowel_type=v_type,
                    has_anusvara=has_anusvara,
                    has_chandrabindu=has_chandrabindu,
                    has_visarga=has_visarga,
                    is_cluster_onset=(consonant_count > 1 and not has_final_halant),
                    precedes_cluster=False,
                    word_index=word_idx,
                    is_word_final=is_final,
                    ambiguous=ambiguous,
                    ambiguity_reason=ambiguity_reason,
                )
            )
            continue

        # Non-Devanagari or miscellaneous character
        i += 1

    return sylls
