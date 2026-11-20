"""Generate-and-Verify loop: Google Gemini candidate generation + deterministic meter verification."""

import logging

from app.config import settings
from app.errors import (
    GeminiAuthError,
    GeminiNotConfiguredError,
    GeminiProviderError,
    GeminiRateLimitError,
    GeminiTimeoutError,
    InvalidMeterRequestError,
)
from app.llm.client import LLMClient
from app.llm.prompts import build_rewrite_system_prompt, build_rewrite_user_prompt
from app.meter.scanner import scan_line
from app.meter.templates import get_template
from app.rhyme.endings import are_rhymes
from app.schemas import RewriteRequest, RewriteResponse, Suggestion

logger = logging.getLogger(__name__)


async def generate_verified_suggestions(
    request: RewriteRequest,
    client: LLMClient | None = None,
) -> RewriteResponse:
    """
    Core AI workflow:
    1. Server resolves and validates the correct target for the selected charan.
    2. Deterministic baseline scan of original broken line.
    3. Google Gemini proposes candidate rewrites via Interactions API.
    4. Python meter engine scans every candidate.
    5. Failed or non-matching candidates are strictly discarded.
    6. Retries up to MAX_RETRIES until sufficient verified candidates are found.
    7. Returns ONLY deterministically verified lines.
    """
    # 1. Server-side Charan Target Resolution & Validation
    try:
        tmpl = get_template(request.selected_meter, request.custom_pattern)
        if not tmpl.charan_targets:
            raise InvalidMeterRequestError("Meter has no valid charan targets.")
        expected_target = tmpl.charan_targets[request.charan_index % len(tmpl.charan_targets)]
    except Exception as exc:
        raise InvalidMeterRequestError(f"Failed to resolve meter target: {exc}") from exc

    if request.target_matra_count != expected_target:
        raise InvalidMeterRequestError(
            f"Target mismatch: Charan {request.charan_index + 1} of {request.selected_meter} "
            f"requires {expected_target} matras, but request specified {request.target_matra_count}."
        )

    # 2. Check Gemini Configuration
    llm = client or LLMClient()
    if not llm.is_configured:
        raise GeminiNotConfiguredError()

    # 3. Deterministic baseline scan of the original line
    current_scan = scan_line(
        text=request.original_line,
        target_matras=expected_target,
        charan_index=request.charan_index,
        meter_name=request.selected_meter,
        pronunciation_mode=request.pronunciation_mode,
    )

    verified_suggestions: list[Suggestion] = []
    seen_lines: set[str] = {request.original_line.strip()}
    max_attempts = settings.MAX_RETRIES
    attempts_made = 0

    system_prompt = build_rewrite_system_prompt()
    user_prompt = build_rewrite_user_prompt(request, current_scan)

    while attempts_made < max_attempts and len(verified_suggestions) < request.max_suggestions:
        attempts_made += 1
        try:
            candidates = await llm.generate_candidates(
                prompt=user_prompt,
                system_instruction=system_prompt,
                max_candidates=request.max_suggestions + 2,
            )
        except (
            GeminiTimeoutError,
            GeminiAuthError,
            GeminiRateLimitError,
            GeminiNotConfiguredError,
            GeminiProviderError,
        ):
            raise
        except Exception as exc:
            logger.warning(f"Gemini attempt {attempts_made} failed: {exc}")
            if attempts_made >= max_attempts and not verified_suggestions:
                raise
            break

        for cand_text, cand_note in candidates:
            clean_text = cand_text.strip()
            if not clean_text or clean_text in seen_lines:
                continue

            seen_lines.add(clean_text)

            # 4. Strict Deterministic Meter Verification
            cand_scan = scan_line(
                text=clean_text,
                target_matras=expected_target,
                charan_index=request.charan_index,
                meter_name=request.selected_meter,
                pronunciation_mode=request.pronunciation_mode,
            )

            # Verification rule: MUST exactly match the required matra count
            if cand_scan.status != "matched" or cand_scan.actual_matras != expected_target:
                # REJECT: Meter condition violated
                continue

            # If phonetic mode detected unresolved pronunciation ambiguities, discard
            if cand_scan.status == "ambiguous":
                continue

            # 5. Optional rhyme check
            rhyme_compat = None
            if request.rhyme_requirement:
                rhyme_compat = are_rhymes(clean_text, request.rhyme_requirement)

            verified_suggestions.append(
                Suggestion(
                    suggested_line=clean_text,
                    calculated_matra_count=cand_scan.actual_matras,
                    target_matra_count=expected_target,
                    verified_status=True,
                    rhyme_compatibility=rhyme_compat,
                    meaning_note=cand_note or "Matches target rhythm",
                    syllables=cand_scan.syllables,
                    verification_details={
                        "break_positions": cand_scan.break_positions,
                        "diagnostics": cand_scan.diagnostics,
                        "meter": request.selected_meter,
                    },
                )
            )

            if len(verified_suggestions) >= request.max_suggestions:
                break

    message = (
        "Verified alternatives found."
        if verified_suggestions
        else "No verified rewrite found. Try changing the instructions."
    )

    return RewriteResponse(
        suggestions=verified_suggestions,
        message=message,
        attempts_made=attempts_made,
        attempts_used=attempts_made,
        provider="gemini",
    )
