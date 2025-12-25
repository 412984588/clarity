import re
import unicodedata

_WORD_SEP = r"(?:[\W_]+)"
_INNER_SEP = r"(?:[\W_]*)"
_LEET_MAP = {
    "a": "a4@",
    "e": "e3",
    "i": "i1!",
    "o": "o0",
    "s": "s5$",
    "t": "t7",
}


def _char_pattern(ch: str) -> str:
    variants = _LEET_MAP.get(ch.lower())
    if not variants:
        return re.escape(ch)
    escaped = "".join(re.escape(v) for v in variants)
    return f"[{escaped}]"


def _split_word(word: str) -> str:
    # 处理分词/分割攻击，允许单词内被空白或标点打断
    return _INNER_SEP.join(_char_pattern(ch) for ch in word)


def _split_phrase(*words: str) -> str:
    return _WORD_SEP.join(_split_word(word) for word in words)


def _prefix_boundary(pattern: str) -> str:
    return rf"(?<!\w){pattern}"


DANGEROUS_PATTERNS = [
    _prefix_boundary(
        rf"{_split_word('ignore')}{_WORD_SEP}(?:{_split_word('all')}{_WORD_SEP})?{_split_word('previous')}(?:{_WORD_SEP}{_split_word('instructions')})?"
    ),
    _prefix_boundary(
        rf"{_split_word('disregard')}{_WORD_SEP}(?:{_split_word('all')}{_WORD_SEP})?"
    ),
    _prefix_boundary(
        rf"{_split_word('forget')}{_WORD_SEP}(?:{_split_word('all')}{_WORD_SEP})?"
    ),
    _prefix_boundary(
        rf"{_split_word('please')}{_WORD_SEP}{_split_word('ignore')}(?:{_WORD_SEP}{_split_word('previous')}(?:{_WORD_SEP}{_split_word('instructions')})?)?"
    ),
    _prefix_boundary(
        rf"{_split_word('override')}{_WORD_SEP}(?:{_split_word('all')}{_WORD_SEP})?(?:{_split_word('previous')}{_WORD_SEP})?{_split_word('instructions')}"
    ),
    _prefix_boundary(rf"{_split_phrase('now', 'act', 'as')}"),
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


def _normalize_content(content: str) -> str:
    # Unicode 归一化，减少全角/兼容字符混淆
    return unicodedata.normalize("NFKC", content)


def sanitize_user_input(content: str) -> str:
    sanitized = _normalize_content(content)
    for regex in _DANGEROUS_REGEXES:
        sanitized = regex.sub("", sanitized)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized


def strip_pii(content: str) -> str:
    sanitized = _EMAIL_RE.sub("", content)
    sanitized = _PHONE_RE.sub("", sanitized)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized
