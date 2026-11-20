"""Meter template definitions for Doha, Chaupai, and Custom patterns."""

from dataclasses import dataclass, field

from app.errors import InvalidCustomPatternError, InvalidMeterError


@dataclass(frozen=True)
class MeterTemplate:
    """Definition and constraints of a matrik meter."""

    name: str
    display_name: str
    language: str
    charan_targets: list[int]
    description: str
    yati_metadata: list[str] = field(default_factory=list)
    allowed_variants: list[list[int]] = field(default_factory=list)


DOHA_TEMPLATE = MeterTemplate(
    name="doha",
    display_name="दोहा (Doha)",
    language="hindi",
    charan_targets=[13, 11, 13, 11],
    description="अर्धसम मात्रिक छंद: विषम चरण (1, 3) में 13 मात्राएँ, सम चरण (2, 4) में 11 मात्राएँ। यति 13 और 11 पर।",
    yati_metadata=["13 पर यति", "11 पर यति (तुक)", "13 पर यति", "11 पर यति (तुक)"],
    allowed_variants=[],
)

CHAUPAI_TEMPLATE = MeterTemplate(
    name="chaupai",
    display_name="चौपाई (Chaupai)",
    language="hindi",
    charan_targets=[16, 16, 16, 16],
    description="सम मात्रिक छंद: प्रत्येक चरण में 16 मात्राएँ। चरण के अंत में जगण (।ऽ।) या तगण (ऽऽ।) वर्जित माना जाता है।",
    yati_metadata=["16 पर यति", "16 पर यति (तुक)", "16 पर यति", "16 पर यति (तुक)"],
    allowed_variants=[],
)

BUILTIN_TEMPLATES: dict[str, MeterTemplate] = {
    "doha": DOHA_TEMPLATE,
    "chaupai": CHAUPAI_TEMPLATE,
}


def get_template(meter_name: str, custom_pattern: list[int] | None = None) -> MeterTemplate:
    """
    Retrieves or constructs the requested meter template.
    Strictly validates custom patterns.
    """
    cleaned_name = (meter_name or "").strip().lower()

    if cleaned_name in BUILTIN_TEMPLATES:
        return BUILTIN_TEMPLATES[cleaned_name]

    if cleaned_name == "custom":
        if not custom_pattern or not isinstance(custom_pattern, list):
            raise InvalidCustomPatternError(
                "A non-empty list of integer matra targets is required for custom meters."
            )
        if len(custom_pattern) == 0:
            raise InvalidCustomPatternError("Custom pattern cannot be empty.")
        for val in custom_pattern:
            if not isinstance(val, int) or val <= 0:
                raise InvalidCustomPatternError(
                    f"Each matra target in custom pattern must be a positive integer, got: {val}"
                )

        return MeterTemplate(
            name="custom",
            display_name="कस्टम छंद (Custom Meter)",
            language="hindi",
            charan_targets=list(custom_pattern),
            description=f"कस्टम मात्रिक छंद: चरण विभाजन {' | '.join(str(x) for x in custom_pattern)} मात्राएँ।",
            yati_metadata=[f"{x} पर यति" for x in custom_pattern],
            allowed_variants=[],
        )

    raise InvalidMeterError(
        f"Unknown meter '{meter_name}'. Supported meters: 'doha', 'chaupai', 'custom'."
    )
