"""Hindi meter-aware rewrite prompts for Google Gemini."""

from app.schemas import LineResult, RewriteRequest


def build_rewrite_system_prompt() -> str:
    return (
        "You are a Hindi poetry co-writer. Your task is to suggest natural Devanagari lines that preserve "
        "the writer's intended meaning while attempting to match a specified matra-based poetic meter. "
        "You do not determine whether a line is metrically correct. A separate deterministic meter engine "
        "performs that validation.\n\n"
        "WRITING GUIDELINES:\n"
        "1. Write natural, grammatically correct Hindi in Devanagari script.\n"
        "2. Preserve the writer's original core meaning, imagery, and emotional tone.\n"
        "3. Aim to match the exact target matra count by adjusting phrasing, synonyms, or word order.\n"
        "4. Avoid forced, obscure, or unnatural vocabulary.\n"
        "5. Avoid meaningless filler words added solely to manipulate syllable count.\n"
        "6. If a rhyme constraint is specified, ensure the line naturally concludes with a compatible rhyming sound.\n"
        "7. Return multiple diverse alternatives in the requested structured JSON schema."
    )


def build_rewrite_user_prompt(
    request: RewriteRequest,
    current_scan: LineResult,
) -> str:
    diagnosis_str = (
        "\n".join(f"- {d}" for d in current_scan.diagnostics) or "- Line violates meter target."
    )
    syllable_summary = " ".join(f"{s.text}({s.weight})" for s in current_scan.syllables)
    rhyme_inst = (
        f"Rhyme requirement: The ending must rhyme with '{request.rhyme_requirement}'."
        if request.rhyme_requirement
        else "No specific rhyme constraint."
    )
    poet_inst = (
        f"Writer's guidance: '{request.instructions}'"
        if request.instructions
        else "Preserve the original meaning and tone closely."
    )

    # Human-readable 1-based section number
    section_num = request.charan_index + 1

    return (
        f"POEM CONTEXT:\n"
        f"- Selected Meter: {request.selected_meter}\n"
        f"- Section: Section {section_num} (चरण {section_num})\n"
        f'- Original Line: "{request.original_line}"\n'
        f"- Current Matra Count: {current_scan.actual_matras}\n"
        f"- Required Target Matras: {request.target_matra_count}\n"
        f"- Current Scansion: {syllable_summary}\n"
        f"- Current Diagnostics:\n{diagnosis_str}\n"
        f"- {poet_inst}\n"
        f"- {rhyme_inst}\n\n"
        f"TASK:\n"
        f"Provide up to {request.max_suggestions + 2} natural Hindi alternative lines that attempt to reach "
        f"exactly {request.target_matra_count} matras while preserving the meaning."
    )


def build_rhyme_prompt(word: str, count: int = 8) -> str:
    return (
        f"Generate {count} common, natural Hindi poetic words in Devanagari that rhyme with '{word}'.\n"
        "Return structured JSON."
    )
