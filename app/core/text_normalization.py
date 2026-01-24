# ============================================
# AGTR v6.0 - Text Normalization & Spam Detection
# Dosya: app/core/text_normalization.py
# Unicode normalization, homoglyph detection, leetspeak detection
# ============================================

import re
import unicodedata
from typing import Dict, List, Tuple


# ============ Homoglyph Mappings ============

# Cyrillic to Latin lookalikes
CYRILLIC_HOMOGLYPHS = {
    "а": "a",  # Cyrillic a
    "е": "e",  # Cyrillic e
    "о": "o",  # Cyrillic o
    "р": "p",  # Cyrillic r
    "с": "c",  # Cyrillic c
    "у": "y",  # Cyrillic y
    "х": "x",  # Cyrillic x
    "А": "A",
    "В": "B",
    "Е": "E",
    "К": "K",
    "М": "M",
    "Н": "H",
    "О": "O",
    "Р": "P",
    "С": "C",
    "Т": "T",
    "Х": "X",
}

# Greek to Latin lookalikes
GREEK_HOMOGLYPHS = {
    "α": "a",
    "β": "b",
    "ε": "e",
    "ι": "i",
    "ο": "o",
    "ρ": "p",
    "υ": "y",
    "Α": "A",
    "Β": "B",
    "Ε": "E",
    "Ι": "I",
    "Κ": "K",
    "Μ": "M",
    "Ν": "N",
    "Ο": "O",
    "Ρ": "P",
    "Τ": "T",
    "Υ": "Y",
    "Ζ": "Z",
}

# Special character homoglyphs
SPECIAL_HOMOGLYPHS = {
    "Ⅰ": "I",
    "Ⅱ": "II",
    "Ⅲ": "III",
    "Ⅳ": "IV",
    "Ⅴ": "V",
    "ⅰ": "i",
    "ⅱ": "ii",
    "ⅲ": "iii",
    "ⅳ": "iv",
    "ⅴ": "v",
    "①": "1",
    "②": "2",
    "③": "3",
    "④": "4",
    "⑤": "5",
    "⓪": "0",
    "⓵": "1",
    "⓶": "2",
    "⓷": "3",
    "⓸": "4",
    "⓹": "5",
}

# Combine all homoglyphs
ALL_HOMOGLYPHS = {**CYRILLIC_HOMOGLYPHS, **GREEK_HOMOGLYPHS, **SPECIAL_HOMOGLYPHS}

# ============ Leetspeak Mappings ============

LEETSPEAK_MAP = {
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "8": "b",
    "@": "a",
    "$": "s",
    "|": "i",
    "!": "i",
    "+": "t",
    "€": "e",
    "£": "l",
    "¥": "y",
    "₹": "r",
}

# Advanced leetspeak patterns (multi-char substitutions)
LEETSPEAK_PATTERNS = [
    (r"ph", "f"),
    (r"kk", "ck"),
    (r"xx", "x"),
    (r"ck", "k"),
    (r"\|\/\|", "m"),  # |\/| = M
    (r"\|\|", "n"),  # || = N
    (r"\|_", "l"),  # |_ = L
    (r"\/\/", "w"),  # \/\/ = W
    (r"\(\)", "o"),  # () = O
]


# ============ Unicode Normalization ============


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode text to NFC (Canonical Composition)

    Args:
        text: Input text

    Returns:
        Normalized text

    Example:
        "café" (é = e + combining accent) → "café" (é as single character)
    """
    if not text:
        return text
    # NFC = Canonical decomposition followed by canonical composition
    return unicodedata.normalize("NFC", text)


def remove_accents(text: str) -> str:
    """
    Remove accents from text

    Args:
        text: Input text

    Returns:
        Text without accents

    Example:
        "café" → "cafe"
        "naïve" → "naive"
    """
    if not text:
        return text
    # NFD = Canonical decomposition
    nfd = unicodedata.normalize("NFD", text)
    # Remove combining characters (accents)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def normalize_whitespace(text: str) -> str:
    """
    Normalize all whitespace to single space

    Args:
        text: Input text

    Returns:
        Text with normalized whitespace
    """
    if not text:
        return text
    # Replace all whitespace (including nbsp, tabs, etc.) with single space
    return re.sub(r"\s+", " ", text).strip()


# ============ Homoglyph Detection ============


def replace_homoglyphs(text: str) -> str:
    """
    Replace homoglyphs (lookalike characters) with ASCII equivalents

    Args:
        text: Input text

    Returns:
        Text with homoglyphs replaced

    Example:
        "hеllo" (e is Cyrillic) → "hello"
        "аdmin" (a is Cyrillic) → "admin"
    """
    if not text:
        return text

    result = []
    for char in text:
        # Check if character is a known homoglyph
        if char in ALL_HOMOGLYPHS:
            result.append(ALL_HOMOGLYPHS[char])
        else:
            result.append(char)

    return "".join(result)


def detect_homoglyphs(text: str) -> Tuple[bool, List[str]]:
    """
    Detect if text contains homoglyphs

    Args:
        text: Input text

    Returns:
        Tuple of (has_homoglyphs, list_of_homoglyphs_found)
    """
    if not text:
        return False, []

    homoglyphs_found = []
    for char in text:
        if char in ALL_HOMOGLYPHS:
            homoglyphs_found.append(f"{char} → {ALL_HOMOGLYPHS[char]}")

    return len(homoglyphs_found) > 0, homoglyphs_found


# ============ Leetspeak Detection ============


def decode_leetspeak(text: str) -> str:
    """
    Decode leetspeak to normal text

    Args:
        text: Input text

    Returns:
        Text with leetspeak decoded

    Example:
        "h3ll0 w0rld" → "hello world"
        "@dm1n" → "admin"
    """
    if not text:
        return text

    result = text.lower()

    # Apply pattern replacements first (multi-char)
    for pattern, replacement in LEETSPEAK_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Apply single character replacements
    for leet_char, normal_char in LEETSPEAK_MAP.items():
        result = result.replace(leet_char, normal_char)

    return result


def detect_leetspeak(text: str) -> Tuple[bool, int, str]:
    """
    Detect if text contains leetspeak

    Args:
        text: Input text

    Returns:
        Tuple of (has_leetspeak, leet_char_count, decoded_text)
    """
    if not text:
        return False, 0, text

    leet_count = 0
    for char in text:
        if char in LEETSPEAK_MAP:
            leet_count += 1

    decoded = decode_leetspeak(text)
    has_leetspeak = leet_count > 0 or decoded != text.lower()

    return has_leetspeak, leet_count, decoded


# ============ Combined Normalization ============


def normalize_text_aggressive(text: str) -> str:
    """
    Aggressively normalize text for spam detection

    Steps:
    1. Unicode normalization (NFC)
    2. Remove accents
    3. Replace homoglyphs
    4. Decode leetspeak
    5. Normalize whitespace
    6. Lowercase

    Args:
        text: Input text

    Returns:
        Normalized text for comparison

    Example:
        "Hеll0 W0rld! @dmin" → "hello world admin"
        (e is Cyrillic, 0s are leetspeak, @ is leetspeak)
    """
    if not text:
        return ""

    # Step 1: Unicode normalization
    text = normalize_unicode(text)

    # Step 2: Remove accents
    text = remove_accents(text)

    # Step 3: Replace homoglyphs
    text = replace_homoglyphs(text)

    # Step 4: Decode leetspeak
    text = decode_leetspeak(text)

    # Step 5: Normalize whitespace
    text = normalize_whitespace(text)

    # Step 6: Lowercase
    text = text.lower()

    return text


def get_text_variants(text: str) -> List[str]:
    """
    Generate multiple normalized variants of text for spam matching

    Returns:
        List of text variants (original, normalized, without spaces, etc.)
    """
    if not text:
        return []

    variants = []

    # Original
    variants.append(text.lower())

    # Normalized
    normalized = normalize_text_aggressive(text)
    variants.append(normalized)

    # Without spaces
    variants.append(normalized.replace(" ", ""))

    # Without special chars
    alphanumeric = re.sub(r"[^a-z0-9]", "", normalized)
    variants.append(alphanumeric)

    # Without numbers
    alpha_only = re.sub(r"\d", "", normalized)
    variants.append(alpha_only)

    # Remove duplicates
    return list(set(variants))


# ============ Text Analysis ============


def analyze_text_for_spam(text: str) -> Dict:
    """
    Comprehensive text analysis for spam detection

    Args:
        text: Input text

    Returns:
        Dict with analysis results
    """
    if not text:
        return {
            "original": "",
            "normalized": "",
            "has_homoglyphs": False,
            "has_leetspeak": False,
            "variants": [],
        }

    # Detect homoglyphs
    has_homoglyphs, homoglyphs = detect_homoglyphs(text)

    # Detect leetspeak
    has_leetspeak, leet_count, decoded = detect_leetspeak(text)

    # Normalize
    normalized = normalize_text_aggressive(text)

    # Generate variants
    variants = get_text_variants(text)

    return {
        "original": text,
        "normalized": normalized,
        "has_homoglyphs": has_homoglyphs,
        "homoglyphs_found": homoglyphs,
        "has_leetspeak": has_leetspeak,
        "leet_char_count": leet_count,
        "decoded_text": decoded,
        "variants": variants,
        "suspicious": has_homoglyphs or (has_leetspeak and leet_count > 2),
    }


# ============ Turkish-Specific Normalization ============


def normalize_turkish(text: str) -> str:
    """
    Normalize Turkish characters

    Args:
        text: Turkish text

    Returns:
        Text with Turkish chars normalized to ASCII-compatible
    """
    if not text:
        return text

    turkish_map = {
        "ı": "i",
        "İ": "I",
        "ş": "s",
        "Ş": "S",
        "ğ": "g",
        "Ğ": "G",
        "ü": "u",
        "Ü": "U",
        "ö": "o",
        "Ö": "O",
        "ç": "c",
        "Ç": "C",
    }

    for tr_char, en_char in turkish_map.items():
        text = text.replace(tr_char, en_char)

    return text
