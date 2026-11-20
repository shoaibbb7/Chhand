"""Integration tests for FastAPI REST API endpoints."""

from fastapi.testclient import TestClient


def test_health_endpoint(test_client: TestClient):
    res = test_client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "ok")
    assert "version" in data
    # Ensure no secrets in health check
    assert "GEMINI_API_KEY" not in str(data)
    assert "LLM_API_KEY" not in str(data)


def test_analyze_endpoint_valid_doha(test_client: TestClient):
    payload = {
        "meter": "doha",
        "charans": [
            "मन का दीपक जब जले",
            "मिटे अँधेरा दूर",
            "सीख सदा सच की रखो",
            "साथ रहेगा नूर",
        ],
        "pronunciation_mode": "orthographic",
    }
    res = test_client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["overall_status"] == "matched"
    assert len(data["lines"]) == 4
    assert data["lines"][0]["actual_matras"] == 13
    assert data["lines"][1]["actual_matras"] == 11


def test_analyze_endpoint_broken_line(test_client: TestClient):
    payload = {
        "meter": "doha",
        "charans": [
            "मन का दीपक जब जले",
            "साथ रहेगा फिर नूर",  # Over by 2
        ],
    }
    res = test_client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["lines"][1]["status"] == "over"
    assert data["lines"][1]["difference"] == 2


def test_rhyme_endpoint(test_client: TestClient):
    payload = {"word": "नूर", "limit": 6}
    res = test_client.post("/api/rhyme", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["original_word"] == "नूर"
    assert data["rhyme_tail"] == "ूर"
    # 'दूर' and 'ज़रूर' should be in exact matches from dictionary
    assert "दूर" in data["exact_matches"]
    assert "ज़रूर" in data["exact_matches"]


def test_rhyme_families_endpoint(test_client: TestClient):
    res = test_client.get("/api/rhyme/families")
    assert res.status_code == 200
    data = res.json()
    assert "families" in data
    assert len(data["families"]) >= 5
    endings = [f["ending"] for f in data["families"]]
    assert "-ूर" in endings or "-ार" in endings


def test_rewrite_endpoint_when_llm_unconfigured(test_client: TestClient, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    payload = {
        "original_line": "साथ रहेगा फिर नूर",
        "target_matra_count": 11,
        "selected_meter": "doha",
        "charan_index": 1,
    }
    res = test_client.post("/api/rewrite", json=payload)
    # When Gemini key is not configured, should return 503 GEMINI_NOT_CONFIGURED cleanly
    assert res.status_code == 503
    data = res.json()
    assert data["error"]["code"] in ("GEMINI_NOT_CONFIGURED", "LLM_NOT_CONFIGURED")


def test_rewrite_endpoint_success(test_client: TestClient, monkeypatch):
    from app.api import rewrite
    from app.schemas import RewriteResponse, Suggestion

    async def fake_verify(request):
        return RewriteResponse(
            suggestions=[
                Suggestion(
                    suggested_line="साथ रहेगा नूर",
                    calculated_matra_count=11,
                    target_matra_count=11,
                    verified_status=True,
                    meaning_note="Drops 'फिर'",
                )
            ],
            message="Verified alternatives found.",
            attempts_made=1,
        )

    monkeypatch.setattr(rewrite, "generate_verified_suggestions", fake_verify)

    payload = {
        "original_line": "साथ रहेगा फिर नूर",
        "target_matra_count": 11,
        "selected_meter": "doha",
        "charan_index": 1,
    }
    res = test_client.post("/api/rewrite", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["suggestions"]) == 1
    assert data["suggestions"][0]["suggested_line"] == "साथ रहेगा नूर"
    assert data["suggestions"][0]["calculated_matra_count"] == 11
    assert data["suggestions"][0]["verified_status"] is True


def test_invalid_meter_error(test_client: TestClient):
    payload = {
        "meter": "unsupported_meter_xyz",
        "charans": ["मन का दीपक जब जले"],
    }
    res = test_client.post("/api/analyze", json=payload)
    assert res.status_code == 422 or res.status_code == 400
