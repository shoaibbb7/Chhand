"""Unit tests for the Google Gemini generate-and-verify workflow with mocked SDK."""

import pytest

from app.errors import (
    GeminiAuthError,
    GeminiNotConfiguredError,
    GeminiProviderError,
    GeminiRateLimitError,
    GeminiTimeoutError,
    InvalidMeterRequestError,
)
from app.llm.verify_loop import generate_verified_suggestions
from app.schemas import RewriteRequest


@pytest.mark.asyncio
async def test_missing_api_key_raises_controlled_error(mock_llm_client):
    client = mock_llm_client(is_configured=False)
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    with pytest.raises(GeminiNotConfiguredError):
        await generate_verified_suggestions(req, client=client)


@pytest.mark.asyncio
async def test_valid_candidate_accepted(mock_llm_client):
    # Candidate "साथ रहेगा नूर" has exactly 11 matras
    client = mock_llm_client(
        response_data={"candidates": [{"line": "साथ रहेगा नूर", "note": "Drops 'फिर'"}]}
    )
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 1
    assert resp.suggestions[0].suggested_line == "साथ रहेगा नूर"
    assert resp.suggestions[0].calculated_matra_count == 11
    assert resp.suggestions[0].target_matra_count == 11
    assert resp.suggestions[0].verified_status is True
    assert resp.provider == "gemini"


@pytest.mark.asyncio
async def test_invalid_candidate_strictly_rejected(mock_llm_client):
    # Candidate "साथ रहेगा फिर नूर" has 13 matras, target is 11
    client = mock_llm_client(
        response_data={
            "candidates": [{"line": "साथ रहेगा फिर नूर", "note": "Unchanged broken candidate"}]
        }
    )
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    # MUST BE REJECTED!
    assert len(resp.suggestions) == 0
    assert "No verified rewrite found" in resp.message


@pytest.mark.asyncio
async def test_never_trust_llm_self_reported_count(mock_llm_client):
    # Candidate claims in note that it is 11 matras, but text has 13 matras
    client = mock_llm_client(
        response_data={
            "candidates": [
                {
                    "line": "साथ रहेगा फिर नूर",
                    "note": "AI claims: Exactly 11 matras",
                }
            ]
        }
    )
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    # Must be strictly rejected by the deterministic engine
    assert len(resp.suggestions) == 0


@pytest.mark.asyncio
async def test_mixed_candidates_filtered_strictly(mock_llm_client):
    # 1st candidate is invalid (13 matras), 2nd is valid (11 matras: "साथ रहे फिर नूर"), 3rd is invalid
    client = mock_llm_client(
        response_data={
            "candidates": [
                {"line": "साथ रहेगा फिर नूर", "note": "13 matras (invalid)"},
                {"line": "साथ रहे फिर नूर", "note": "11 matras (valid)"},
                {"line": "साथ रहेगा और भी नूर", "note": "15 matras (invalid)"},
            ]
        }
    )
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 1
    assert resp.suggestions[0].suggested_line == "साथ रहे फिर नूर"
    assert resp.suggestions[0].calculated_matra_count == 11


@pytest.mark.asyncio
async def test_charan_1_doha_target_13(mock_llm_client):
    # Charan 1 of Doha requires 13 matras
    # "मन का दीपक जब जले" has 13 matras
    client = mock_llm_client(
        response_data={"candidates": [{"line": "मन का दीपक जब जले", "note": "13 matras"}]}
    )
    req = RewriteRequest(
        original_line="दीपक जब जले",
        target_matra_count=13,
        selected_meter="doha",
        charan_index=0,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 1
    assert resp.suggestions[0].target_matra_count == 13
    assert resp.suggestions[0].calculated_matra_count == 13


@pytest.mark.asyncio
async def test_charan_4_doha_target_11(mock_llm_client):
    # Charan 4 of Doha (index 3) requires 11 matras
    client = mock_llm_client(
        response_data={"candidates": [{"line": "मिटे अँधेरा दूर", "note": "11 matras"}]}
    )
    req = RewriteRequest(
        original_line="मिटे अँधेरा बहुत दूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=3,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 1
    assert resp.suggestions[0].target_matra_count == 11
    assert resp.suggestions[0].calculated_matra_count == 11


@pytest.mark.asyncio
async def test_custom_meter_target_14_for_third_charan(mock_llm_client):
    # Custom pattern [12, 12, 14, 12], third charan (index 2) requires 14 matras
    # "सीख सदा सच बात रखो" -> 2 + 1 + 1 + 2 + 1 + 1 + 2 + 1 + 1 + 2 = 14
    cand = "सीख सदा सच बात रखो"
    client = mock_llm_client(response_data={"candidates": [{"line": cand, "note": "14 matras"}]})
    req = RewriteRequest(
        original_line="सीख सदा सच की रखो",
        target_matra_count=14,
        selected_meter="custom",
        custom_pattern=[12, 12, 14, 12],
        charan_index=2,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 1
    assert resp.suggestions[0].target_matra_count == 14
    assert resp.suggestions[0].calculated_matra_count == 14


@pytest.mark.asyncio
async def test_target_mismatch_rejected_server_side(mock_llm_client):
    # Client requests 14 for Doha charan 1 (which requires 13)
    client = mock_llm_client()
    req = RewriteRequest(
        original_line="मन का दीपक जब जले",
        target_matra_count=14,  # Conflicting with Doha charan 1 target (13)
        selected_meter="doha",
        charan_index=0,
    )
    with pytest.raises(InvalidMeterRequestError):
        await generate_verified_suggestions(req, client=client)


@pytest.mark.asyncio
async def test_duplicates_removed(mock_llm_client):
    client = mock_llm_client(
        response_data={
            "candidates": [
                {"line": "साथ रहेगा नूर", "note": "Attempt 1"},
                {"line": "साथ रहेगा नूर", "note": "Duplicate"},
            ]
        }
    )
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 1


@pytest.mark.asyncio
async def test_empty_candidates_handled(mock_llm_client):
    client = mock_llm_client(response_data={"candidates": []})
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 0
    assert "No verified rewrite found" in resp.message


@pytest.mark.asyncio
async def test_gemini_auth_failure_propagates(mock_llm_client):
    client = mock_llm_client(should_auth_fail=True)
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    with pytest.raises(GeminiAuthError):
        await generate_verified_suggestions(req, client=client)


@pytest.mark.asyncio
async def test_gemini_rate_limit_propagates(mock_llm_client):
    client = mock_llm_client(should_rate_limit=True)
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    with pytest.raises(GeminiRateLimitError):
        await generate_verified_suggestions(req, client=client)


@pytest.mark.asyncio
async def test_gemini_timeout_propagates(mock_llm_client):
    client = mock_llm_client(should_timeout=True)
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    with pytest.raises(GeminiTimeoutError):
        await generate_verified_suggestions(req, client=client)


@pytest.mark.asyncio
async def test_gemini_provider_error_propagates(mock_llm_client):
    client = mock_llm_client(should_fail=True)
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    with pytest.raises(GeminiProviderError):
        await generate_verified_suggestions(req, client=client)
