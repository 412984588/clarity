import re

DANGEROUS_PATTERNS = [
    r"ignore\s+(all\s+)?previous",
    r"disregard\s+(all\s+)?",
    r"forget\s+(all\s+)?",
    r"^system:",
    r"^assistant:",
    r"\[INST\]",
    r"<\|im_start\|>",
]

_DANGEROUS_REGEXES = [
    re.compile(pattern, flags=re.IGNORECASE | re.MULTILINE)
    for pattern in DANGEROUS_PATTERNS
]

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{4}"
)


def sanitize_user_input(content: str) -> str:
    sanitized = content
    for regex in _DANGEROUS_REGEXES:
        sanitized = regex.sub("", sanitized)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized


def strip_pii(content: str) -> str:
    sanitized = _EMAIL_RE.sub("", content)
    sanitized = _PHONE_RE.sub("", sanitized)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized
