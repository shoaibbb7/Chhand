"""Unit tests for meter scanner, multi-charan analysis, and error diagnosis."""

from app.meter.scanner import scan_charan, scan_poem
from app.meter.templates import CHAUPAI_TEMPLATE, DOHA_TEMPLATE


def test_scan_exact_match_doha_charan_1():
    # 13 matras
    res = scan_charan("मन का दीपक जब जले", target_matras=13, charan_index=0)
    assert res.status == "matched"
    assert res.actual_matras == 13
    assert res.difference == 0
    assert len(res.break_positions) == 0
    assert res.overflow_span is None


def test_scan_exact_match_doha_charan_2():
    # 11 matras
    res = scan_charan("मिटे अँधेरा दूर", target_matras=11, charan_index=1)
    assert res.status == "matched"
    assert res.actual_matras == 11
    assert res.difference == 0


def test_scan_overcount_with_break_and_overflow():
    # "साथ रहेगा फिर नूर" has 13 matras, target is 11
    res = scan_charan("साथ रहेगा फिर नूर", target_matras=11, charan_index=1)
    assert res.status == "over"
    assert res.actual_matras == 13
    assert res.difference == 2
    assert len(res.break_positions) > 0
    assert res.overflow_span is not None
    # Overflow diagnostic contains "Over by 2"
    assert any("Over by 2" in d for d in res.diagnostics)


def test_scan_undercount():
    # "मिटे अँधेरा" has 8 matras, target is 11
    res = scan_charan("मिटे अँधेरा", target_matras=11, charan_index=1)
    assert res.status == "under"
    assert res.actual_matras == 8
    assert res.difference == -3
    assert any("Under by 3" in d for d in res.diagnostics)


def test_scan_invalid_characters():
    res = scan_charan("मन का deepak जब जले", target_matras=13, charan_index=0)
    assert res.status == "invalid"
    assert any("Unsupported non-Devanagari" in d for d in res.diagnostics)


def test_full_doha_scan_poem():
    charans = [
        "मन का दीपक जब जले",
        "मिटे अँधेरा दूर",
        "सीख सदा सच की रखो",
        "साथ रहेगा नूर",
    ]
    resp = scan_poem(charans, DOHA_TEMPLATE)
    assert resp.overall_status == "matched"
    assert len(resp.lines) == 4
    for line in resp.lines:
        assert line.status == "matched"


def test_full_chaupai_scan_poem():
    charans = [
        "जय हनुमान ज्ञान गुन सागर",
        "जय कपीस तिहुँ लोक उजागर",
        "राम दूत अतुलित बल धामा",
        "अंजनि पुत्र पवनसुत नामा",
    ]
    resp = scan_poem(charans, CHAUPAI_TEMPLATE)
    assert resp.overall_status == "matched"
    assert len(resp.lines) == 4
    for line in resp.lines:
        assert line.status == "matched"
        assert line.actual_matras == 16


def test_reviewed_dohas_from_dataset(sample_dohas):
    reviewed = [d for d in sample_dohas if d.get("validation_status") == "reviewed"]
    assert len(reviewed) >= 3
    for doha in reviewed:
        resp = scan_poem(doha["charans"], DOHA_TEMPLATE)
        assert resp.overall_status == "matched", f"Failed for {doha['id']}: {doha['charans']}"


def test_reviewed_chaupais_from_dataset(sample_chaupais):
    reviewed = [c for c in sample_chaupais if c.get("validation_status") == "reviewed"]
    assert len(reviewed) >= 2
    for chaupai in reviewed:
        resp = scan_poem(chaupai["charans"], CHAUPAI_TEMPLATE)
        assert resp.overall_status == "matched", f"Failed for {chaupai['id']}: {chaupai['charans']}"


def test_broken_examples_from_dataset(broken_examples):
    assert len(broken_examples) >= 10
    for example in broken_examples:
        res = scan_charan(
            text=example["modified_text"],
            target_matras=example["expected_target"],
            charan_index=example["charan_index"],
        )
        assert res.status == example["expected_status"], f"Failed status for {example['id']}"
        assert res.actual_matras == example["expected_actual"], (
            f"Failed actual count for {example['id']}"
        )
        assert any(example["expected_diagnostic_fragment"] in d for d in res.diagnostics)
