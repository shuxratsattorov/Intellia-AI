import re
from dataclasses import dataclass
from __future__ import annotations


class SafetyError(ValueError):
    pass

ALLOWED_DOC_TYPES = {"report", "presentation"}
ALLOWED_LEVELS = {"school", "college", "university", "master", "phd"}
ALLOWED_LENGTH = {"short", "medium", "long"}
ALLOWED_LANG = {"uz", "ru", "en"}


LIMITS = {
    "topic_max": 200,              # Generate form -> Topic
    "keywords_max": 200,           # Keywords input
    "requirements_max": 1200,      # Advanced options
    "selection_max": 6000,         # Editor: rewrite
    "summarize_max": 8000,         # Editor: summarize
    "shorten_max": 9000,           # Editor: shorten
    "context_sentence_max": 300,   # Synonyms context
    "word_max": 60,                # Synonyms word
}


INJECTION_PATTERNS = [
    # -------------------------
    # instruction override
    # -------------------------
    r"\bignore\b.*\binstructions?\b",
    r"\bdisregard\b.*\binstructions?\b",
    r"\bforget\b.*\b(previous|earlier)\b.*\b(rules?|instructions?)\b",

    # -------------------------
    # system / developer
    # -------------------------
    r"\bsystem\b.*\bprompt\b",
    r"\bdeveloper\b.*\bmessage\b",
    r"\bhidden\b.*\b(instructions?|prompt)\b",
    r"\breveal\b.*\b(the\s+)?(prompt|instructions?|policy)\b",

    # -------------------------
    # roleplay bypass
    # -------------------------
    r"\bpretend\b.*\byou\b.*\bare\b",
    r"\bact\b.*\bas\b.*\bunrestricted\b",
    r"\bno\b.*\blimitations?\b",

    # -------------------------
    # jailbreak
    # -------------------------
    r"\bDAN\b",
    r"\bdo\b.*\banything\b.*\bnow\b",
    r"\bjailbreak\b",

    # -------------------------
    # policy bypass
    # -------------------------
    r"\bbypass\b.*\bpolicy\b",
    r"\bignore\b.*\bpolicy\b",
    r"\bcontent\b.*\bpolicy\b",
]


def _has_injection(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in INJECTION_PATTERNS)

def normalize(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text

def _ensure_len(name: str, value: str, max_len: int) -> str:
    value = normalize(value)

    if not value:
        raise SafetyError(f"{name} is required.")

    if len(value) > max_len:
        raise SafetyError(f"{name} is too long (max {max_len} chars).")

    if _has_injection(value):
        raise SafetyError(f"Suspicious instructions detected in {name}.")

    return value


def _ensure_optional_len(name: str, value: str | None, max_len: int) -> str:
    if value is None:
        return "None"

    value = normalize(value)

    if not value:
        return "None"

    if len(value) > max_len:
        raise SafetyError(f"{name} is too long (max {max_len} chars).")

    if _has_injection(value):
        raise SafetyError(f"Suspicious instructions detected in {name}.")

    return value


def _ensure_in_set(name: str, value: str, allowed: set[str]) -> str:
    v = normalize(value).lower()

    if v not in allowed:
        raise SafetyError(f"Invalid {name}. Allowed: {sorted(allowed)}")

    return v


# =====================================================
# 7) Generate endpoint uchun SAFE DTO
# =====================================================
@dataclass(frozen=True)
class GenerateSafeInput:
    """
    Validatsiyadan o'tgan, AI'ga yuborishga XAVFSIZ input.
    """
    topic: str
    education_level: str
    doc_type: str
    length: str
    language: str
    keywords: str
    requirements: str


# =====================================================
# 8) /ai/generate uchun validator
# =====================================================
def validate_generate(
    *,
    topic: str,
    education_level: str,
    doc_type: str,
    length: str,
    language: str = "uz",
    keywords: str | None = None,
    requirements: str | None = None,
) -> GenerateSafeInput:
    """
    Generate formdan kelgan hamma inputni tekshiradi.
    """

    safe_topic = _ensure_len("topic", topic, LIMITS["topic_max"])
    safe_level = _ensure_in_set("education_level", education_level, ALLOWED_LEVELS)
    safe_type = _ensure_in_set("doc_type", doc_type, ALLOWED_DOC_TYPES)
    safe_length = _ensure_in_set("length", length, ALLOWED_LENGTH)
    safe_lang = _ensure_in_set("language", language, ALLOWED_LANG)

    safe_keywords = _ensure_optional_len("keywords", keywords, LIMITS["keywords_max"])
    safe_requirements = _ensure_optional_len(
        "requirements", requirements, LIMITS["requirements_max"]
    )

    # AI service faqat SHU obyekt bilan ishlaydi
    return GenerateSafeInput(
        topic=safe_topic,
        education_level=safe_level,
        doc_type=safe_type,
        length=safe_length,
        language=safe_lang,
        keywords=safe_keywords,
        requirements=safe_requirements,
    )


# =====================================================
# 9) /ai/summarize
# =====================================================
def validate_summarize(*, text: str, language: str = "uz") -> tuple[str, str]:
    safe_text = _ensure_len("text", text, LIMITS["summarize_max"])
    safe_lang = _ensure_in_set("language", language, ALLOWED_LANG)
    return safe_text, safe_lang


# =====================================================
# 10) /ai/rewrite-selection
# =====================================================
def validate_rewrite_selection(
    *,
    text: str,
    language: str = "uz",
    goal: str = "clarity",
) -> tuple[str, str, str]:
    safe_text = _ensure_len("text", text, LIMITS["selection_max"])
    safe_lang = _ensure_in_set("language", language, ALLOWED_LANG)

    safe_goal = normalize(goal).lower()
    if len(safe_goal) > 32:
        raise SafetyError("goal is too long.")
    if _has_injection(safe_goal):
        raise SafetyError("Suspicious instructions detected in goal.")

    return safe_text, safe_lang, safe_goal


# =====================================================
# 11) /ai/shorten
# =====================================================
def validate_shorten(
    *,
    text: str,
    language: str = "uz",
    reduction: str = "30%",
) -> tuple[str, str, str]:
    safe_text = _ensure_len("text", text, LIMITS["shorten_max"])
    safe_lang = _ensure_in_set("language", language, ALLOWED_LANG)

    # reduction faqat "20%" ko'rinishida bo'lishi shart
    red = normalize(reduction)
    if not re.fullmatch(r"\d{1,3}%", red):
        raise SafetyError("reduction must look like '20%' or '40%'.")

    pct = int(red[:-1])
    if pct < 10 or pct > 80:
        raise SafetyError("reduction must be between 10% and 80%.")

    return safe_text, safe_lang, red


# =====================================================
# 12) /ai/synonyms
# =====================================================
def validate_synonyms(
    *,
    word: str,
    context_sentence: str,
    language: str = "uz",
) -> tuple[str, str, str]:
    safe_word = _ensure_len("word", word, LIMITS["word_max"])
    safe_ctx = _ensure_len(
        "context_sentence", context_sentence, LIMITS["context_sentence_max"]
    )
    safe_lang = _ensure_in_set("language", language, ALLOWED_LANG)

    return safe_word, safe_ctx, safe_lang
