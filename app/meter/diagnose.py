"""Deterministic diagnostic generation for meter scansion errors."""

from typing import Literal


def generate_diagnostics(
    actual_matras: int,
    target_matras: int,
    status: Literal["matched", "over", "under", "ambiguous", "invalid"],
    overflow_text: str | None = None,
    unsupported_chars: list[str] | None = None,
    ambiguities: list[str] | None = None,
    charan_index: int = 0,
    meter_name: str = "doha",
    break_syllable_indices: list[int] | None = None,
    total_syllables: int = 0,
) -> list[str]:
    """Generates clear, deterministic, human-readable explanations of meter status."""
    diagnostics: list[str] = []

    if status == "invalid":
        if unsupported_chars:
            unique_chars = sorted(set(unsupported_chars))
            diagnostics.append(
                f"Unsupported non-Devanagari characters found: {', '.join(repr(c) for c in unique_chars[:5])}."
            )
        else:
            diagnostics.append("Invalid or unparseable input.")
        return diagnostics

    if status == "ambiguous":
        diagnostics.append(
            "Pronunciation ambiguity detected: some syllables have variable meter weight in modern recitation."
        )
        if ambiguities:
            for amb in ambiguities[:3]:
                diagnostics.append(f"• {amb}")
        return diagnostics

    diff = actual_matras - target_matras
    is_even_charan = charan_index % 2 == 1
    half_desc = "second half (सम चरण)" if is_even_charan else "first half (विषम चरण)"

    if status == "matched":
        diagnostics.append(
            f"Line matches exact target of {target_matras} matras for {meter_name} ({half_desc})."
        )
    elif status == "over":
        msg = f"The line contains {actual_matras} matras, but the target is {target_matras}. Over by {diff}."
        if break_syllable_indices and total_syllables > 0:
            first_break = break_syllable_indices[0]
            if first_break >= total_syllables // 2:
                portion = "final portion"
            elif first_break == 0:
                portion = "initial portion"
            else:
                portion = "middle portion"
            if overflow_text and overflow_text.strip():
                msg += f" The additional contribution occurs in the {portion} of the charan starting at '{overflow_text.strip()}'."
            else:
                msg += f" The additional contribution occurs in the {portion} of the charan."
        elif overflow_text and overflow_text.strip():
            msg += f" The additional contribution occurs in the final portion of the charan starting at '{overflow_text.strip()}'."
        else:
            msg += " The additional contribution occurs in the final portion of the charan."
        diagnostics.append(msg)
    elif status == "under":
        missing = abs(diff)
        if actual_matras == 0:
            diagnostics.append(f"Empty or incomplete charan: requires {target_matras} matras.")
        else:
            diagnostics.append(
                f"The line contains {actual_matras} matras, but the target is {target_matras}. Under by {missing}: needs {missing} more matra{'s' if missing > 1 else ''} to complete this charan."
            )

    return diagnostics
