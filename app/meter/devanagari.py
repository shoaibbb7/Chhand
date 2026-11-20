"""Devanagari Unicode character classification and properties."""

import unicodedata

# Unicode constants for Devanagari
DEVANAGARI_RANGE = (0x0900, 0x097F)
EXTENDED_DEVANAGARI_RANGE = (0xA8E0, 0xA8FF)

# Vowel classifications
SHORT_VOWELS = {"अ", "इ", "उ", "ऋ", "ऌ"}
LONG_VOWELS = {"आ", "ई", "ऊ", "ए", "ऐ", "ओ", "औ", "ऍ", "ऑ", "ऎ", "ऒ"}
ALL_INDEPENDENT_VOWELS = SHORT_VOWELS | LONG_VOWELS

# Dependent vowel signs (Matras)
SHORT_MATRAS = {
    "\u093f",  # ि (i)
    "\u0941",  # ु (u)
    "\u0943",  # ृ (ri)
    "\u0946",  # ॆ (short e)
    "\u094a",  # ॊ (short o)
}

LONG_MATRAS = {
    "\u093e",  # ा (aa)
    "\u0940",  # ी (ee)
    "\u0942",  # ू (oo)
    "\u0944",  # ॄ (long ri)
    "\u0945",  # ॅ (candra e)
    "\u0947",  # े (e)
    "\u0948",  # ै (ai)
    "\u0949",  # ॉ (candra o)
    "\u094b",  # ो (o)
    "\u094c",  # ौ (au)
}

ALL_MATRAS = SHORT_MATRAS | LONG_MATRAS

# Modifier signs
VIRAMA = "\u094d"  # ् (halant)
NUKTA = "\u093c"  # ़
ANUSVARA = "\u0902"  # ं
CHANDRABINDU = "\u0901"  # ँ
VISARGA = "\u0903"  # ः
AVAGRAHA = "\u093d"  # ऽ

# Dandas
DANDA = "\u0964"  # ।
DOUBLE_DANDA = "\u0965"  # ॥
DANDAS = {DANDA, DOUBLE_DANDA, "|"}

# Consonants (standard range 0x0915 to 0x0939, plus 0x0958-0x095F nukta consonants, and 0x0933, 0x0934)
CONSONANTS = (
    {chr(cp) for cp in range(0x0915, 0x093A)}
    | {chr(cp) for cp in range(0x0958, 0x0960)}
    | {"\u0933", "\u0934"}
)


def is_devanagari(char: str) -> bool:
    """Returns True if the character is within Devanagari Unicode blocks."""
    if not char:
        return False
    cp = ord(char[0])
    return (
        DEVANAGARI_RANGE[0] <= cp <= DEVANAGARI_RANGE[1]
        or EXTENDED_DEVANAGARI_RANGE[0] <= cp <= EXTENDED_DEVANAGARI_RANGE[1]
    )


def is_independent_vowel(char: str) -> bool:
    return char in ALL_INDEPENDENT_VOWELS


def is_short_vowel(char: str) -> bool:
    return char in SHORT_VOWELS


def is_long_vowel(char: str) -> bool:
    return char in LONG_VOWELS


def is_consonant(char: str) -> bool:
    return char in CONSONANTS


def is_matra(char: str) -> bool:
    return char in ALL_MATRAS


def is_short_matra(char: str) -> bool:
    return char in SHORT_MATRAS


def is_long_matra(char: str) -> bool:
    return char in LONG_MATRAS


def is_halant(char: str) -> bool:
    return char == VIRAMA


def is_nukta(char: str) -> bool:
    return char == NUKTA


def is_anusvara(char: str) -> bool:
    return char == ANUSVARA


def is_chandrabindu(char: str) -> bool:
    return char == CHANDRABINDU


def is_visarga(char: str) -> bool:
    return char == VISARGA


def is_danda(char: str) -> bool:
    return char in DANDAS


def classify_char(char: str) -> str:
    """Classifies a single character into Devanagari structural types."""
    if not char:
        return "empty"
    if char.isspace():
        return "whitespace"
    if is_danda(char):
        return "punctuation_danda"
    if is_halant(char):
        return "halant"
    if is_nukta(char):
        return "nukta"
    if is_anusvara(char):
        return "anusvara"
    if is_chandrabindu(char):
        return "chandrabindu"
    if is_visarga(char):
        return "visarga"
    if is_short_matra(char):
        return "short_matra"
    if is_long_matra(char):
        return "long_matra"
    if is_short_vowel(char):
        return "short_vowel"
    if is_long_vowel(char):
        return "long_vowel"
    if is_consonant(char):
        return "consonant"
    if char == AVAGRAHA:
        return "avagraha"
    if unicodedata.category(char).startswith("P"):
        return "punctuation"
    return "unsupported"
