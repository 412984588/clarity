"""危机检测服务 - 识别用户消息中的危机信号"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

# 危机关键词（多语言）
CRISIS_KEYWORDS: Dict[str, List[str]] = {
    "en": [
        "suicide",
        "kill myself",
        "end my life",
        "want to die",
        "self-harm",
        "hurt myself",
        "cut myself",
        "cutting myself",
        "no reason to live",
        "better off dead",
        "can't go on",
    ],
    "es": [
        "suicidio",
        "matarme",
        "quitarme la vida",
        "quiero morir",
        "autolesión",
        "hacerme daño",
        "cortarme",
        "no tengo razón para vivir",
        "mejor muerto",
        "no puedo seguir",
    ],
}

# 危机热线资源
CRISIS_RESOURCES: Dict[str, str] = {
    "US": "988",  # Suicide & Crisis Lifeline
    "ES": "717 003 717",  # Teléfono de la Esperanza (Spain)
}


@dataclass
class CrisisCheckResult:
    """危机检测结果"""

    blocked: bool
    reason: Optional[str] = None
    resources: Optional[Dict[str, str]] = None
    matched_keyword: Optional[str] = None


def _build_patterns() -> List[re.Pattern]:
    """构建所有语言的关键词正则"""
    patterns = []
    for lang_keywords in CRISIS_KEYWORDS.values():
        for keyword in lang_keywords:
            # 使用 word boundary 避免误匹配
            pattern = re.compile(
                rf"\b{re.escape(keyword)}\b",
                flags=re.IGNORECASE,
            )
            patterns.append(pattern)
    return patterns


_CRISIS_PATTERNS = _build_patterns()


def detect_crisis(content: str) -> CrisisCheckResult:
    """
    检测用户消息中的危机信号

    Args:
        content: 用户消息内容

    Returns:
        CrisisCheckResult: 包含是否阻止、原因和资源信息
    """
    content_lower = content.lower()

    for pattern in _CRISIS_PATTERNS:
        match = pattern.search(content_lower)
        if match:
            return CrisisCheckResult(
                blocked=True,
                reason="CRISIS",
                resources=CRISIS_RESOURCES,
                matched_keyword=match.group(0),
            )

    return CrisisCheckResult(blocked=False)


def get_crisis_response() -> Dict:
    """获取危机响应的标准格式"""
    return {
        "blocked": True,
        "reason": "CRISIS",
        "resources": CRISIS_RESOURCES,
        "message": "We noticed you might be going through a difficult time. "
        "Please reach out to a crisis helpline for immediate support.",
    }
