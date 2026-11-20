"""Unit tests for Laghu and Guru weight assignment."""

from app.meter.normalize import normalize_devanagari
from app.meter.syllables import split_syllables
from app.meter.weights import assign_weights


def get_weights_for_text(text: str, overrides: dict | None = None):
    norm = normalize_devanagari(text)
    sylls = split_syllables(norm)
    details = assign_weights(sylls, overrides)
    return [(d.text, d.weight, d.classification, d.reason) for d in details]


def test_short_and_long_vowels():
    # लघु: 1, गुरु: 2
    res = get_weights_for_text("दिन रात")
    weights = [r[1] for r in res]
    # दिन -> दि(1) + न(1) = 2
    # रात -> रा(2) + त(1) = 3
    assert weights == [1, 1, 2, 1]


def test_chandrabindu_remains_laghu():
    # अँधेरा: अँ(1) + धे(2) + रा(2) = 5
    res = get_weights_for_text("अँधेरा")
    weights = [r[1] for r in res]
    assert weights == [1, 2, 2]
    assert res[0][2] == "laghu"
    assert res[0][3] == "short_vowel_chandrabindu"


def test_anusvara_makes_guru():
    # हंस vs हँस
    # हंस: हं(2) + स(1) = 3
    res_anusvara = get_weights_for_text("हंस")
    assert [r[1] for r in res_anusvara] == [2, 1]
    assert res_anusvara[0][2] == "guru"

    # हँस: हँ(1) + स(1) = 2
    res_chandra = get_weights_for_text("हँस")
    assert [r[1] for r in res_chandra] == [1, 1]
    assert res_chandra[0][2] == "laghu"


def test_visarga_makes_guru():
    # दुःख: दुः(2) + ख(1) = 3
    res = get_weights_for_text("दुःख")
    assert [r[1] for r in res] == [2, 1]
    assert res[0][2] == "guru"


def test_conjunct_lengthening():
    # सत्य: स is short, but precedes conjunct cluster त्य -> स becomes Guru (2)!
    res = get_weights_for_text("सत्य")
    assert [r[1] for r in res] == [2, 1]
    assert res[0][3] == "preceding_conjunct"


def test_initial_conjunct_does_not_lengthen_nonexistent_prev():
    # प्यार: प्या(2) + र(1) = 3
    res = get_weights_for_text("प्यार")
    assert [r[1] for r in res] == [2, 1]


def test_manual_overrides():
    # Force 'मन' second syllable to weight 2
    res = get_weights_for_text("मन", overrides={"1": 2})
    assert [r[1] for r in res] == [1, 2]
    assert res[1][3] == "manual_override"


def test_cumulative_weights_in_details():
    # काके लागूं पाय: का(2) के(2) ला(2) गूं(2) पा(2) य(1)
    norm = normalize_devanagari("काके लागूं पाय")
    sylls = split_syllables(norm)
    details = assign_weights(sylls)
    weights = [d.weight for d in details]
    cumulatives = [d.cumulative for d in details]
    assert weights == [2, 2, 2, 2, 2, 1]
    assert cumulatives == [2, 4, 6, 8, 10, 11]
