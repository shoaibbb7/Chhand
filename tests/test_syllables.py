"""Unit tests for syllable and akshara segmentation."""

from app.meter.normalize import normalize_devanagari
from app.meter.syllables import split_syllables


def test_segment_simple_words():
    norm = normalize_devanagari("मन का दीपक")
    sylls = split_syllables(norm)
    texts = [s.text for s in sylls]
    assert texts == ["म", "न", "का", "दी", "प", "क"]
    assert sylls[0].vowel_type == "inherent"
    assert sylls[1].vowel_type == "inherent"
    assert sylls[2].vowel_type == "long"
    assert sylls[3].vowel_type == "long"


def test_chandrabindu_vs_anusvara():
    norm = normalize_devanagari("अँधेरा और संसार")
    sylls = split_syllables(norm)
    texts = [s.text for s in sylls]
    assert "अँ" in texts
    andh_syll = next(s for s in sylls if s.text == "अँ")
    assert andh_syll.has_chandrabindu is True
    assert andh_syll.has_anusvara is False

    san_syll = next(s for s in sylls if s.text == "सं")
    assert san_syll.has_anusvara is True


def test_conjunct_detection():
    norm = normalize_devanagari("सत्य और प्यार")
    sylls = split_syllables(norm)
    # सत्य has 'स' and 'त्य'
    satya_sylls = [s for s in sylls if s.word_index == 0]
    assert len(satya_sylls) == 2
    assert satya_sylls[0].text == "स"
    assert satya_sylls[0].precedes_cluster is True  # Preceding cluster marked
    assert satya_sylls[1].text == "त्य"
    assert satya_sylls[1].is_cluster_onset is True

    # प्यार has cluster onset
    pyar_sylls = [s for s in sylls if s.word_index == 2]
    assert pyar_sylls[0].text == "प्या"
    assert pyar_sylls[0].is_cluster_onset is True


def test_source_spans_preserved():
    text = "सीख सदा सच की रखो"
    norm = normalize_devanagari(text)
    sylls = split_syllables(norm)
    for s in sylls:
        extracted = text[s.orig_start : s.orig_end]
        assert extracted == s.text


def test_phonetic_mode_ambiguity():
    norm = normalize_devanagari("कमल")
    sylls_ortho = split_syllables(norm, mode="orthographic")
    assert not any(s.ambiguous for s in sylls_ortho)

    sylls_phonetic = split_syllables(norm, mode="phonetic")
    # In phonetic mode, word-final unhalanted schwa is marked as ambiguous
    final_syll = sylls_phonetic[-1]
    assert final_syll.ambiguous is True
