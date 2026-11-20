"""Deterministic scansion and meter evaluation engine."""

from typing import Any, Literal

from app.meter.devanagari import is_danda, is_devanagari
from app.meter.diagnose import generate_diagnostics
from app.meter.normalize import normalize_devanagari
from app.meter.syllables import split_syllables
from app.meter.templates import MeterTemplate
from app.meter.weights import assign_weights
from app.schemas import AnalyzeResponse, LineResult, SyllableDetail


def scan_charan(
    text: str,
    target_matras: int,
    charan_index: int = 0,
    meter_name: str = "doha",
    pronunciation_mode: Literal["orthographic", "phonetic", "manual"] = "orthographic",
    pronunciation_overrides: dict[str, Any] | None = None,
) -> LineResult:
    """
    Scans a single Hindi charan against a target matra count deterministically.
    """
    raw_text = text or ""
    norm_res = normalize_devanagari(raw_text)
    normalized = norm_res.normalized

    # 1. Check for unsupported characters
    unsupported_chars: list[str] = []
    for ch in normalized:
        if ch.isspace() or is_danda(ch) or ch in {",", ";", ":", "-", "!", "?", '"', "'", "।", "॥"}:
            continue
        if not is_devanagari(ch):
            unsupported_chars.append(ch)

    if unsupported_chars:
        diag = generate_diagnostics(
            actual_matras=0,
            target_matras=target_matras,
            status="invalid",
            unsupported_chars=unsupported_chars,
            charan_index=charan_index,
            meter_name=meter_name,
        )
        return LineResult(
            charan_index=charan_index,
            original_text=raw_text,
            normalized_text=normalized,
            target_matras=target_matras,
            actual_matras=0,
            difference=-target_matras,
            status="invalid",
            syllables=[],
            individual_weights=[],
            cumulative_weights=[],
            character_spans=[],
            break_positions=[],
            overflow_span=None,
            diagnostics=diag,
            pronunciation_notes=[],
        )

    # 2. Syllable segmentation
    raw_syllables = split_syllables(norm_res, mode=pronunciation_mode)

    # 3. Weight calculation
    syllable_details: list[SyllableDetail] = assign_weights(
        raw_syllables, pronunciation_overrides=pronunciation_overrides
    )

    # 4. Compute cumulative counts, breaks, and overflow
    individual_weights = [s.weight for s in syllable_details]
    cumulative_weights: list[int] = []
    running_total = 0
    break_positions: list[int] = []
    overflow_start_char: int | None = None
    overflow_end_char: int | None = None

    for idx, w in enumerate(individual_weights):
        running_total += w
        cumulative_weights.append(running_total)
        if running_total > target_matras:
            break_positions.append(idx)
            if overflow_start_char is None:
                overflow_start_char = syllable_details[idx].start
            overflow_end_char = syllable_details[idx].end

    actual_matras = running_total
    difference = actual_matras - target_matras

    # 5. Determine status
    ambiguities = [s.ambiguity_reason for s in raw_syllables if s.ambiguous]
    if ambiguities and pronunciation_mode == "phonetic":
        status_val: Literal["matched", "over", "under", "ambiguous", "invalid"] = "ambiguous"
    elif difference == 0 and actual_matras > 0:
        status_val = "matched"
    elif difference > 0:
        status_val = "over"
    else:
        status_val = "under"

    # Overflow text extraction for diagnostic message
    overflow_text = None
    overflow_span = None
    if overflow_start_char is not None and overflow_end_char is not None:
        overflow_span = [overflow_start_char, overflow_end_char]
        overflow_text = raw_text[overflow_start_char:overflow_end_char]

    diagnostics = generate_diagnostics(
        actual_matras=actual_matras,
        target_matras=target_matras,
        status=status_val,
        overflow_text=overflow_text,
        ambiguities=ambiguities,
        charan_index=charan_index,
        meter_name=meter_name,
        break_syllable_indices=break_positions,
        total_syllables=len(syllable_details),
    )

    character_spans = [[s.start, s.end] for s in syllable_details]

    return LineResult(
        charan_index=charan_index,
        original_text=raw_text,
        normalized_text=normalized,
        target_matras=target_matras,
        actual_matras=actual_matras,
        difference=difference,
        status=status_val,
        syllables=syllable_details,
        individual_weights=individual_weights,
        cumulative_weights=cumulative_weights,
        character_spans=character_spans,
        break_positions=break_positions,
        overflow_span=overflow_span,
        diagnostics=diagnostics,
        pronunciation_notes=ambiguities,
    )


def scan_line(
    text: str,
    target_matras: int,
    charan_index: int = 0,
    meter_name: str = "doha",
    pronunciation_mode: Literal["orthographic", "phonetic", "manual"] = "orthographic",
    pronunciation_overrides: dict[str, Any] | None = None,
) -> LineResult:
    """Convenience alias for scanning a single line/charan."""
    return scan_charan(
        text=text,
        target_matras=target_matras,
        charan_index=charan_index,
        meter_name=meter_name,
        pronunciation_mode=pronunciation_mode,
        pronunciation_overrides=pronunciation_overrides,
    )


def scan_poem(
    charans: list[str],
    template: MeterTemplate,
    pronunciation_mode: Literal["orthographic", "phonetic", "manual"] = "orthographic",
    pronunciation_overrides: dict[str, Any] | None = None,
) -> AnalyzeResponse:
    """
    Scans a multi-charan stanza (e.g. 4 charans for Doha/Chaupai) against a template.
    """
    targets = template.charan_targets
    line_results: list[LineResult] = []

    # Pad or slice charans to match template target length
    num_charans = max(len(charans), len(targets))
    all_empty = True

    for i in range(num_charans):
        text = charans[i] if i < len(charans) else ""
        if text.strip():
            all_empty = False
        target = targets[i] if i < len(targets) else targets[-1]
        res = scan_charan(
            text=text,
            target_matras=target,
            charan_index=i,
            meter_name=template.name,
            pronunciation_mode=pronunciation_mode,
            pronunciation_overrides=pronunciation_overrides,
        )
        line_results.append(res)

    # Determine overall status
    if all_empty:
        overall_status = "incomplete"
        summary = "No lines entered yet."
    elif any(r.status == "invalid" for r in line_results):
        overall_status = "invalid"
        summary = "One or more lines contain invalid non-Devanagari characters."
    elif any(r.status == "ambiguous" for r in line_results):
        overall_status = "ambiguous"
        summary = "Poem contains lines with pronunciation ambiguity."
    elif any(
        r.status == "under" and r.actual_matras == 0
        for r in line_results
        if r.charan_index < len(targets)
    ):
        overall_status = "incomplete"
        summary = "Poem is partially entered."
    elif all(r.status == "matched" for r in line_results[: len(targets)]):
        overall_status = "matched"
        summary = f"All {len(targets)} charans strictly match the {template.display_name} meter."
    else:
        overall_status = "needs_revision"
        failed_count = sum(1 for r in line_results[: len(targets)] if r.status != "matched")
        summary = f"{failed_count} line{'s' if failed_count > 1 else ''} need{'s' if failed_count == 1 else ''} attention to fit {template.display_name}."

    return AnalyzeResponse(
        overall_status=overall_status,
        meter=template.name,
        target_pattern=list(targets),
        lines=line_results,
        summary=summary,
    )
