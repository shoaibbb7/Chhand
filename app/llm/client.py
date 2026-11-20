"""Official Google GenAI SDK client using the asynchronous Interactions API."""

import asyncio
import json
import logging
from typing import Any

from google import genai
from pydantic import BaseModel, Field

from app.config import settings
from app.errors import (
    GeminiAuthError,
    GeminiInvalidResponseError,
    GeminiNotConfiguredError,
    GeminiProviderError,
    GeminiRateLimitError,
    GeminiTimeoutError,
)

logger = logging.getLogger(__name__)


class RewriteCandidateText(BaseModel):
    """Single candidate rewrite text proposed by Gemini."""

    line: str = Field(..., min_length=1, description="Candidate Hindi line in Devanagari")
    note: str = Field(default="", description="Brief explanation of adjustment")


class GeminiRewriteResponse(BaseModel):
    """Structured response expected from Gemini."""

    candidates: list[RewriteCandidateText] = Field(
        default_factory=list, description="List of candidate lines"
    )


class LLMClient:
    """Async client using the official Google GenAI Interactions API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
    ):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.timeout_seconds = timeout_seconds or settings.GEMINI_TIMEOUT_SECONDS
        self._client: genai.Client | None = None

    @property
    def is_configured(self) -> bool:
        """Returns True if a Gemini API key is configured."""
        return bool(self.api_key)

    def _get_genai_client(self) -> genai.Client:
        """Lazily creates and caches the genai.Client."""
        if not self.is_configured:
            raise GeminiNotConfiguredError()

        if self._client is None:
            # v1beta is required for Interactions API access on AI Studio
            self._client = genai.Client(
                api_key=self.api_key,
                http_options={"api_version": "v1beta"},
            )
        return self._client

    async def generate_candidates(
        self,
        prompt: str,
        system_instruction: str | None = None,
        max_candidates: int = 4,
    ) -> list[tuple[str, str]]:
        """
        Calls Gemini Interactions API asynchronously requesting structured JSON output.
        Returns a list of (candidate_line, candidate_note) tuples.
        """
        client = self._get_genai_client()

        # Combine system instruction and user prompt cleanly for Interactions input
        full_input = prompt
        if system_instruction:
            full_input = f"{system_instruction}\n\n{prompt}"

        response_format: dict[str, Any] = {
            "type": "text",
            "mime_type": "application/json",
            "schema": GeminiRewriteResponse.model_json_schema(),
        }

        # Attempt primary model with fast fallback if experiencing high demand / latency
        models_to_try = [self.model]
        if self.model != "gemini-flash-lite-latest":
            models_to_try.append("gemini-flash-lite-latest")

        last_error: Exception | None = None

        for idx, model_name in enumerate(models_to_try):
            has_fallback = idx < len(models_to_try) - 1
            # Primary model gets a tighter timeout (8s) if a fast fallback model is queued
            attempt_timeout = (
                min(self.timeout_seconds, 8.0) if has_fallback else self.timeout_seconds
            )

            try:
                interaction = await asyncio.wait_for(
                    client.aio.interactions.create(
                        model=model_name,
                        input=full_input,
                        response_format=response_format,
                        store=False,  # Stateless request; no server-side conversation history
                        timeout=attempt_timeout,
                    ),
                    timeout=attempt_timeout + 1.0,
                )

                output_text = getattr(interaction, "output_text", None) or ""
                if not output_text.strip():
                    raise GeminiInvalidResponseError("Gemini returned an empty interaction output.")

                try:
                    parsed = GeminiRewriteResponse.model_validate_json(output_text)
                except Exception:
                    logger.warning(
                        "Failed to validate Gemini response schema, attempting JSON fallback."
                    )
                    parsed_dict = json.loads(output_text)
                    cands = parsed_dict.get("candidates", [])
                    return [
                        (
                            (c.get("line") or c.get("text") or "").strip(),
                            (c.get("note") or "").strip(),
                        )
                        for c in cands
                        if (c.get("line") or c.get("text") or "").strip()
                    ]

                return [
                    (c.line.strip(), c.note.strip()) for c in parsed.candidates if c.line.strip()
                ]

            except TimeoutError:
                logger.info(
                    f"Model {model_name} timed out after {attempt_timeout}s, checking fallback."
                )
                last_error = GeminiTimeoutError(
                    f"Gemini request timed out after {attempt_timeout} seconds."
                )
                continue
            except Exception as exc:
                err_str = str(exc)
                if "401" in err_str or "API_KEY_INVALID" in err_str:
                    raise GeminiAuthError("Gemini API key is invalid or unauthorized.") from exc
                elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    raise GeminiRateLimitError() from exc
                elif "503" in err_str and model_name != models_to_try[-1]:
                    # Temporary 503 high demand on primary model, fallback to next model
                    logger.info(
                        f"Model {model_name} returned 503 high demand, falling back to next model."
                    )
                    last_error = exc
                    continue
                else:
                    last_error = GeminiProviderError(f"Gemini provider error: {err_str}")

        if last_error:
            if isinstance(last_error, (GeminiTimeoutError, GeminiAuthError, GeminiRateLimitError)):
                raise last_error
            raise GeminiProviderError(f"Gemini generation failed: {last_error}")

        return []

    async def generate_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Backward-compatible helper for legacy tests and callers."""
        system_inst = ""
        user_prompt = ""
        for m in messages:
            if m.get("role") == "system":
                system_inst = m.get("content", "")
            elif m.get("role") == "user":
                user_prompt = m.get("content", "")

        candidates = await self.generate_candidates(
            prompt=user_prompt,
            system_instruction=system_inst,
        )
        return {"candidates": [{"line": line, "note": note} for line, note in candidates]}
