"""
Emotion Detection Service

Analyzes user message content to detect emotional state.
Returns emotion type and confidence score.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple


class EmotionType(str, Enum):
    """Supported emotion types"""

    ANXIOUS = "anxious"
    SAD = "sad"
    CALM = "calm"
    CONFUSED = "confused"
    NEUTRAL = "neutral"


@dataclass
class EmotionResult:
    """Result of emotion detection"""

    emotion: EmotionType
    confidence: float


# 情绪关键词及其权重
EMOTION_KEYWORDS: Dict[EmotionType, List[Tuple[str, float]]] = {
    EmotionType.ANXIOUS: [
        (r"\bworr(y|ied|ies|ying)\b", 0.8),
        (r"\bscar(ed|y)\b", 0.9),
        (r"\bnervous\b", 0.8),
        (r"\bpanic(k?ing|ked)?\b", 0.95),
        (r"\bstress(ed|ful)?\b", 0.75),
        (r"\banxi(ety|ous)\b", 0.9),
        (r"\boverwhelm(ed|ing)?\b", 0.85),
        (r"\bfreak(ing|ed)?\s*out\b", 0.9),
        (r"\bcan'?t\s+(breathe|calm\s+down)\b", 0.95),
        (r"\bpreocupad[oa]\b", 0.8),  # Spanish
        (r"\bnervios[oa]\b", 0.8),  # Spanish
        (r"\bansiedad\b", 0.9),  # Spanish
        (r"焦虑", 0.85),  # Chinese
        (r"担心", 0.8),  # Chinese
        (r"紧张", 0.8),  # Chinese
    ],
    EmotionType.SAD: [
        (r"\bsad\b", 0.85),
        (r"\bdepress(ed|ing|ion)?\b", 0.95),
        (r"\bhopeless\b", 0.9),
        (r"\bcry(ing)?\b", 0.8),
        (r"\blonely\b", 0.85),
        (r"\bgrief\b", 0.9),
        (r"\bloss\b", 0.7),
        (r"\bhurt(ing)?\b", 0.75),
        (r"\bheartbr(oken|eak)\b", 0.9),
        (r"\bmiserable\b", 0.9),
        (r"\btriste\b", 0.85),  # Spanish
        (r"\bdeprimid[oa]\b", 0.9),  # Spanish
        (r"难过", 0.85),  # Chinese
        (r"伤心", 0.85),  # Chinese
        (r"沮丧", 0.9),  # Chinese
    ],
    EmotionType.CALM: [
        (r"\bpeace(ful)?\b", 0.85),
        (r"\brelax(ed|ing)?\b", 0.8),
        (r"\bcontent(ed)?\b", 0.8),
        (r"\bgrateful\b", 0.85),
        (r"\bhappy\b", 0.75),
        (r"\boptimistic\b", 0.85),
        (r"\bserene\b", 0.9),
        (r"\bthankful\b", 0.8),
        (r"\btranquil[oa]?\b", 0.85),  # Spanish
        (r"\bfeliz\b", 0.75),  # Spanish
        (r"平静", 0.85),  # Chinese
        (r"放松", 0.8),  # Chinese
        (r"快乐", 0.75),  # Chinese
    ],
    EmotionType.CONFUSED: [
        (r"\bconfus(ed|ing)\b", 0.9),
        (r"\bunsure\b", 0.75),
        (r"\blost\b", 0.7),
        (r"\bdon'?t\s+understand\b", 0.85),
        (r"\bunclear\b", 0.8),
        (r"\bpuzzl(ed|ing)\b", 0.8),
        (r"\bwhat\s+should\s+i\s+do\b", 0.75),
        (r"\bi\s+don'?t\s+know\b", 0.7),
        (r"\bconfundid[oa]\b", 0.9),  # Spanish
        (r"\bno\s+entiendo\b", 0.85),  # Spanish
        (r"困惑", 0.9),  # Chinese
        (r"不知道", 0.7),  # Chinese
        (r"迷茫", 0.85),  # Chinese
    ],
}

# 最低置信度阈值
MIN_CONFIDENCE_THRESHOLD = 0.3


def detect_emotion(text: str) -> EmotionResult:
    """
    Analyze text to detect emotional state.

    Args:
        text: User message content

    Returns:
        EmotionResult with detected emotion and confidence score
    """
    if not text or not text.strip():
        return EmotionResult(emotion=EmotionType.NEUTRAL, confidence=0.5)

    text_lower = text.lower()
    emotion_scores: Dict[EmotionType, float] = {}

    for emotion, patterns in EMOTION_KEYWORDS.items():
        total_weight = 0.0
        match_count = 0

        for pattern, weight in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                match_count += len(matches)
                total_weight += weight * len(matches)

        if match_count > 0:
            # 计算该情绪的置信度（权重平均 + 匹配次数加成）
            avg_weight = total_weight / match_count
            # 多次匹配提升置信度，但有上限
            confidence = min(avg_weight * (1 + 0.1 * (match_count - 1)), 1.0)
            emotion_scores[emotion] = confidence

    if not emotion_scores:
        return EmotionResult(emotion=EmotionType.NEUTRAL, confidence=0.5)

    # 找出置信度最高的情绪
    best_emotion = max(emotion_scores, key=lambda e: emotion_scores[e])
    best_confidence = emotion_scores[best_emotion]

    # 如果置信度低于阈值，返回 neutral
    if best_confidence < MIN_CONFIDENCE_THRESHOLD:
        return EmotionResult(emotion=EmotionType.NEUTRAL, confidence=0.5)

    return EmotionResult(emotion=best_emotion, confidence=round(best_confidence, 2))
