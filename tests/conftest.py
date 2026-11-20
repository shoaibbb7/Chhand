"""Pytest configuration and test fixtures for Chhand."""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.meter.templates import CHAUPAI_TEMPLATE, DOHA_TEMPLATE


@pytest.fixture
def test_client() -> TestClient:
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def doha_template():
    return DOHA_TEMPLATE


@pytest.fixture
def chaupai_template():
    return CHAUPAI_TEMPLATE


@pytest.fixture
def sample_dohas() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parent.parent / "data" / "sample_dohas.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


@pytest.fixture
def sample_chaupais() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parent.parent / "data" / "sample_chaupais.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


@pytest.fixture
def broken_examples() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parent.parent / "data" / "broken_examples.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


class MockLLMClient:
    """Mock asynchronous Gemini client for tests without calling external APIs."""

    def __init__(
        self,
        response_data: dict[str, Any] | None = None,
        candidates: list[tuple[str, str]] | None = None,
        should_fail: bool = False,
        should_timeout: bool = False,
        should_auth_fail: bool = False,
        should_rate_limit: bool = False,
        is_configured: bool = True,
    ):
        self.response_data = response_data or {}
        self.candidates = candidates
        self.should_fail = should_fail
        self.should_timeout = should_timeout
        self.should_auth_fail = should_auth_fail
        self.should_rate_limit = should_rate_limit
        self.is_configured = is_configured

    async def generate_candidates(
        self,
        prompt: str,
        system_instruction: str | None = None,
        max_candidates: int = 4,
    ) -> list[tuple[str, str]]:
        if not self.is_configured:
            from app.errors import GeminiNotConfiguredError

            raise GeminiNotConfiguredError()
        if self.should_auth_fail:
            from app.errors import GeminiAuthError

            raise GeminiAuthError("Mock auth error.")
        if self.should_rate_limit:
            from app.errors import GeminiRateLimitError

            raise GeminiRateLimitError()
        if self.should_timeout:
            from app.errors import GeminiTimeoutError

            raise GeminiTimeoutError("Mock timeout exceeded.")
        if self.should_fail:
            from app.errors import GeminiProviderError

            raise GeminiProviderError("Mock provider error.")

        if self.candidates is not None:
            return self.candidates

        cands = self.response_data.get("candidates", [])
        return [(c.get("line") or c.get("text") or "", c.get("note") or "") for c in cands]

    async def generate_json(
        self, messages: list[dict[str, str]], temperature: float = 0.7
    ) -> dict[str, Any]:
        return self.response_data


@pytest.fixture
def mock_llm_client():
    return MockLLMClient
