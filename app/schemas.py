from typing import Any, Literal

from pydantic import BaseModel, Field


class SyllableDetail(BaseModel):
    """Detailed weight and classification for an individual Devanagari syllable."""

    text: str = Field(..., description="Surface text of the syllable/akshara")
    weight: int = Field(..., ge=1, le=2, description="Calculated matra weight (1 or 2)")
    classification: Literal["laghu", "guru"] = Field(
        ..., description="Laghu (1 matra) or Guru (2 matras)"
    )
    start: int = Field(..., ge=0, description="Start character index in original source string")
    end: int = Field(..., ge=0, description="End character index in original source string")
    reason: str = Field(..., description="Phonological justification for weight assignment")
    cumulative: int = Field(default=0, description="Cumulative matra count after this syllable")


class LineResult(BaseModel):
    """Scan and scansion results for a single charan or line."""

    charan_index: int = Field(..., description="0-indexed charan order")
    original_text: str = Field(..., description="Raw input text")
    normalized_text: str = Field(..., description="Unicode normalized text")
    target_matras: int = Field(..., description="Required matra count for this charan")
    actual_matras: int = Field(..., description="Calculated total matra count")
    difference: int = Field(..., description="actual_matras - target_matras")
    status: Literal["matched", "over", "under", "ambiguous", "invalid"] = Field(
        ..., description="Meter evaluation status"
    )
    syllables: list[SyllableDetail] = Field(
        default_factory=list, description="Sequence of decomposed syllables with weights"
    )
    individual_weights: list[int] = Field(
        default_factory=list, description="List of integer weights"
    )
    cumulative_weights: list[int] = Field(
        default_factory=list, description="Running sum of weights after each syllable"
    )
    character_spans: list[list[int]] = Field(
        default_factory=list, description="[start, end] indices in original text"
    )
    break_positions: list[int] = Field(
        default_factory=list, description="Syllable indices where target was exceeded"
    )
    overflow_span: list[int] | None = Field(
        default=None, description="[start, end] char indices of overflow text if over-count"
    )
    diagnostics: list[str] = Field(
        default_factory=list, description="Human-readable scansion diagnostics"
    )
    pronunciation_notes: list[str] = Field(
        default_factory=list, description="Notes on pronunciation assumptions or ambiguities"
    )


class AnalyzeRequest(BaseModel):
    """Payload for meter scanning endpoint."""

    meter: Literal["doha", "chaupai", "custom"] = Field(
        default="doha", description="Target poetic meter"
    )
    charans: list[str] = Field(default_factory=list, description="List of charan lines to analyze")
    custom_pattern: list[int] | None = Field(
        default=None, description="Custom matra target per charan, e.g. [12, 12, 14, 12]"
    )
    pronunciation_mode: Literal["orthographic", "phonetic", "manual"] = Field(
        default="orthographic", description="Schwa and pronunciation evaluation mode"
    )
    pronunciation_overrides: dict[str, Any] | None = Field(
        default=None, description="Optional manual weight overrides by token or position"
    )


class AnalyzeResponse(BaseModel):
    """Aggregate response for poem analysis."""

    overall_status: Literal["matched", "needs_revision", "incomplete", "ambiguous", "invalid"] = (
        Field(..., description="Aggregate status of poem")
    )
    meter: str = Field(..., description="Meter name")
    target_pattern: list[int] = Field(..., description="Target matra counts per charan")
    lines: list[LineResult] = Field(
        default_factory=list, description="Detailed analysis per charan"
    )
    summary: str = Field(..., description="Summary message of the scansion")


class RewriteRequest(BaseModel):
    """Request to generate meter-verified alternative lines."""

    original_line: str = Field(..., description="The broken or original Hindi line")
    target_matra_count: int = Field(..., gt=0, description="Target matra count required")
    selected_meter: str = Field(default="doha", description="Name of the poetic meter")
    charan_index: int = Field(default=0, description="Index of the charan within the stanza")
    custom_pattern: list[int] | None = Field(
        default=None, description="Custom matra target per charan if selected_meter is custom"
    )
    instructions: str = Field(
        default="", description="Poet guidance or specific meaning to preserve"
    )
    rhyme_requirement: str | None = Field(
        default=None, description="Optional target word or ending to rhyme with"
    )
    max_suggestions: int = Field(
        default=3, ge=1, le=5, description="Maximum number of verified suggestions"
    )
    pronunciation_mode: Literal["orthographic", "phonetic", "manual"] = Field(
        default="orthographic", description="Pronunciation mode for verification"
    )


class Suggestion(BaseModel):
    """A candidate rewrite verified strictly by the deterministic engine."""

    suggested_line: str = Field(..., description="The verified Hindi line")
    text: str | None = Field(default=None, description="Alias for suggested_line")
    replacement_line: str | None = Field(default=None, description="Alias for suggested_line")
    calculated_matra_count: int = Field(..., description="Matra count confirmed by engine")
    actual_matras: int | None = Field(default=None, description="Alias for calculated_matra_count")
    actual_matra_count: int | None = Field(
        default=None, description="Alias for calculated_matra_count"
    )
    target_matra_count: int = Field(..., description="Requested target matra count")
    target_matras: int | None = Field(default=None, description="Alias for target_matra_count")
    verified_status: bool = Field(True, description="Always True; only verified lines are returned")
    verified: bool = Field(True, description="Alias for verified_status")
    verification_status: str = Field(default="matched", description="Engine verification status")
    rhyme_compatibility: bool | None = Field(
        default=None, description="True if compatible with rhyme requirement"
    )
    meaning_note: str = Field(default="", description="Explanation of adjustment made")
    explanation: str | None = Field(default=None, description="Alias for meaning_note")
    syllables: list[SyllableDetail] = Field(
        default_factory=list, description="Verified syllable sequence"
    )
    verification_details: dict[str, Any] = Field(
        default_factory=dict, description="Diagnostic data from meter scan"
    )

    def model_post_init(self, __context: Any) -> None:
        if self.text is None:
            self.text = self.suggested_line
        if self.replacement_line is None:
            self.replacement_line = self.suggested_line
        if self.actual_matras is None:
            self.actual_matras = self.calculated_matra_count
        if self.actual_matra_count is None:
            self.actual_matra_count = self.calculated_matra_count
        if self.target_matras is None:
            self.target_matras = self.target_matra_count
        if self.explanation is None:
            self.explanation = self.meaning_note


class RewriteResponse(BaseModel):
    """Verified suggestions response."""

    suggestions: list[Suggestion] = Field(
        default_factory=list, description="Verified suggestions matching target matras"
    )
    message: str = Field(..., description="Status explanation or guidance")
    attempts_made: int = Field(default=1, description="Number of LLM attempts executed")
    attempts_used: int | None = Field(default=None, description="Alias for attempts_made")
    provider: str = Field(default="gemini", description="AI model provider name")

    def model_post_init(self, __context: Any) -> None:
        if self.attempts_used is None:
            self.attempts_used = self.attempts_made


class RhymeRequest(BaseModel):
    """Payload to find Hindi rhyming words."""

    word: str = Field(..., min_length=1, description="Word or line ending to rhyme with")
    limit: int = Field(default=10, ge=1, le=30, description="Max suggestions to return")
    preference: str | None = Field(
        default=None, description="Optional stylistic preference or meter hint"
    )


class RhymeMatch(BaseModel):
    """An individual rhyming word candidate."""

    word: str = Field(..., description="Rhyming Hindi word")
    match_type: Literal["exact", "approximate"] = Field(
        ..., description="Exact phonetic tail or approximate rhyme"
    )
    rhyme_tail: str = Field(..., description="Extracted rhyming sound in Devanagari")
    score: float = Field(default=1.0, description="Relevance / phonological match score")


class RhymeResponse(BaseModel):
    """Response containing rhyming word matches."""

    original_word: str = Field(..., description="Input word")
    rhyme_tail: str = Field(..., description="Normalized phonetic tail")
    exact_matches: list[str] = Field(default_factory=list, description="Words with exact tail")
    approximate_matches: list[str] = Field(
        default_factory=list, description="Words with approximate rhyme"
    )
    all_matches: list[RhymeMatch] = Field(default_factory=list, description="Structured match list")
    category: str = Field(default="", description="Phonetic category descriptor")


class HealthResponse(BaseModel):
    """Application health, version, and provider readiness status."""

    status: str = "ok"
    version: str = "1.0.0"
    meter_engine: dict[str, Any] | str = Field(
        default_factory=lambda: {"available": True}, description="Meter engine availability"
    )
    llm: dict[str, Any] | None = Field(
        default=None, description="LLM provider configuration status"
    )
    llm_configured: bool = Field(default=False, description="Legacy indicator for LLM availability")
    environment: str = "development"
