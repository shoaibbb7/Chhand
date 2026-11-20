"""Unit tests for Devanagari character classification and normalization."""

from app.meter.devanagari import (
    classify_char,
    is_anusvara,
    is_chandrabindu,
    is_consonant,
    is_halant,
    is_independent_vowel,
    is_long_matra,
    is_long_vowel,
    is_matra,
    is_nukta,
    is_short_matra,
    is_short_vowel,
    is_visarga,
)
from app.meter.normalize import normalize_devanagari


def test_independent_vowels():
    assert is_independent_vowel("अ")
    assert is_independent_vowel("आ")
    assert is_independent_vowel("इ")
    assert is_independent_vowel("ई")
    assert is_independent_vowel("उ")
    assert is_independent_vowel("ऊ")
    assert is_independent_vowel("ऋ")
    assert is_independent_vowel("ए")
    assert is_independent_vowel("ऐ")
    assert is_independent_vowel("ओ")
    assert is_independent_vowel("औ")

    assert is_short_vowel("अ")
    assert is_short_vowel("इ")
    assert is_short_vowel("उ")
    assert is_short_vowel("ऋ")

    assert is_long_vowel("आ")
    assert is_long_vowel("ई")
    assert is_long_vowel("ऊ")
    assert is_long_vowel("ए")
    assert is_long_vowel("ऐ")
    assert is_long_vowel("ओ")
    assert is_long_vowel("औ")


def test_consonants():
    for c in [
        "क",
        "ख",
        "ग",
        "घ",
        "च",
        "छ",
        "ज",
        "झ",
        "ट",
        "त",
        "थ",
        "द",
        "ध",
        "न",
        "प",
        "फ",
        "ब",
        "भ",
        "म",
        "य",
        "र",
        "ल",
        "व",
        "श",
        "ष",
        "स",
        "ह",
    ]:
        assert is_consonant(c), f"Expected {c} to be recognized as consonant"
    assert not is_consonant("ा")
    assert not is_consonant("अ")


def test_matras():
    # Short matras
    assert is_matra("ि")
    assert is_short_matra("ि")
    assert is_matra("ु")
    assert is_short_matra("ु")
    assert is_matra("ृ")
    assert is_short_matra("ृ")

    # Long matras
    assert is_matra("ा")
    assert is_long_matra("ा")
    assert is_matra("ी")
    assert is_long_matra("ी")
    assert is_matra("ू")
    assert is_long_matra("ू")
    assert is_matra("े")
    assert is_long_matra("े")
    assert is_matra("ै")
    assert is_long_matra("ै")
    assert is_matra("ो")
    assert is_long_matra("ो")
    assert is_matra("ौ")
    assert is_long_matra("ौ")


def test_modifiers():
    assert is_halant("्")
    assert is_nukta("़")
    assert is_anusvara("ं")
    assert is_chandrabindu("ँ")
    assert is_visarga("ः")


def test_classify_char():
    assert classify_char("क") == "consonant"
    assert classify_char("ा") == "long_matra"
    assert classify_char("ि") == "short_matra"
    assert classify_char("्") == "halant"
    assert classify_char("ं") == "anusvara"
    assert classify_char("ँ") == "chandrabindu"
    assert classify_char("ः") == "visarga"
    assert classify_char(" ") == "whitespace"
    assert classify_char("A") == "unsupported"


def test_unicode_normalization_and_mapping():
    text = "मन का दीपक"
    res = normalize_devanagari(text)
    assert res.normalized == text
    assert len(res.pos_map) == len(text)
    # Mapping span
    start, end = res.map_span(0, 2)
    assert text[start:end] == "मन"
