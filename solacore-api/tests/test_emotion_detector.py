"""Tests for emotion detection service"""

from app.services.emotion_detector import EmotionResult, EmotionType, detect_emotion


class TestEmotionDetector:
    """Test emotion detection functionality"""

    def test_detect_anxious_english(self):
        """Test anxious detection with English text"""
        result = detect_emotion("I'm feeling really worried about my job")
        assert result.emotion == EmotionType.ANXIOUS
        assert result.confidence >= 0.7

    def test_detect_anxious_panic(self):
        """Test anxious detection with panic keywords"""
        result = detect_emotion("I'm panicking, can't calm down")
        assert result.emotion == EmotionType.ANXIOUS
        assert result.confidence >= 0.8

    def test_detect_sad_english(self):
        """Test sad detection with English text"""
        result = detect_emotion("I feel so sad and depressed lately")
        assert result.emotion == EmotionType.SAD
        assert result.confidence >= 0.8

    def test_detect_sad_hopeless(self):
        """Test sad detection with hopeless keyword"""
        result = detect_emotion("Everything feels hopeless")
        assert result.emotion == EmotionType.SAD
        assert result.confidence >= 0.8

    def test_detect_calm_english(self):
        """Test calm detection with English text"""
        result = detect_emotion("I'm feeling peaceful and grateful today")
        assert result.emotion == EmotionType.CALM
        assert result.confidence >= 0.7

    def test_detect_calm_relaxed(self):
        """Test calm detection with relaxed keyword"""
        result = detect_emotion("Finally feeling relaxed and content")
        assert result.emotion == EmotionType.CALM
        assert result.confidence >= 0.7

    def test_detect_confused_english(self):
        """Test confused detection with English text"""
        result = detect_emotion("I'm confused about what to do")
        assert result.emotion == EmotionType.CONFUSED
        assert result.confidence >= 0.8

    def test_detect_confused_unsure(self):
        """Test confused detection with unsure keyword"""
        result = detect_emotion("I don't understand the situation")
        assert result.emotion == EmotionType.CONFUSED
        assert result.confidence >= 0.7

    def test_detect_neutral_no_keywords(self):
        """Test neutral detection when no emotion keywords present"""
        result = detect_emotion("I need to schedule a meeting tomorrow")
        assert result.emotion == EmotionType.NEUTRAL
        assert result.confidence == 0.5

    def test_detect_neutral_empty_text(self):
        """Test neutral detection with empty text"""
        result = detect_emotion("")
        assert result.emotion == EmotionType.NEUTRAL
        assert result.confidence == 0.5

    def test_detect_neutral_whitespace(self):
        """Test neutral detection with whitespace only"""
        result = detect_emotion("   ")
        assert result.emotion == EmotionType.NEUTRAL
        assert result.confidence == 0.5

    def test_detect_spanish_anxious(self):
        """Test anxious detection with Spanish text"""
        result = detect_emotion("Estoy muy preocupado por el examen")
        assert result.emotion == EmotionType.ANXIOUS
        assert result.confidence >= 0.7

    def test_detect_spanish_sad(self):
        """Test sad detection with Spanish text"""
        result = detect_emotion("Me siento muy triste hoy")
        assert result.emotion == EmotionType.SAD
        assert result.confidence >= 0.7

    def test_detect_chinese_anxious(self):
        """Test anxious detection with Chinese text"""
        result = detect_emotion("我很焦虑，担心考试")
        assert result.emotion == EmotionType.ANXIOUS
        assert result.confidence >= 0.7

    def test_detect_chinese_sad(self):
        """Test sad detection with Chinese text"""
        result = detect_emotion("我感到很难过和伤心")
        assert result.emotion == EmotionType.SAD
        assert result.confidence >= 0.7

    def test_detect_chinese_confused(self):
        """Test confused detection with Chinese text"""
        result = detect_emotion("我很困惑，不知道该怎么办")
        assert result.emotion == EmotionType.CONFUSED
        assert result.confidence >= 0.7

    def test_confidence_increases_with_multiple_matches(self):
        """Test that confidence increases with multiple keyword matches"""
        single_result = detect_emotion("I'm worried")
        multi_result = detect_emotion("I'm worried and stressed and anxious")
        assert multi_result.confidence >= single_result.confidence

    def test_highest_confidence_wins(self):
        """Test that highest confidence emotion is selected"""
        # Multiple panic keywords should beat single sad keyword
        result = detect_emotion("I'm panicking panicking panicking and a little sad")
        assert result.emotion == EmotionType.ANXIOUS

    def test_result_dataclass(self):
        """Test EmotionResult dataclass structure"""
        result = EmotionResult(emotion=EmotionType.CALM, confidence=0.85)
        assert result.emotion == EmotionType.CALM
        assert result.confidence == 0.85

    def test_confidence_capped_at_1(self):
        """Test that confidence never exceeds 1.0"""
        # Many matches shouldn't exceed 1.0
        result = detect_emotion(
            "panic panic panic panic panic scared worried anxious stressed"
        )
        assert result.confidence <= 1.0

    def test_case_insensitive(self):
        """Test that detection is case insensitive"""
        lower_result = detect_emotion("i'm worried")
        upper_result = detect_emotion("I'M WORRIED")
        mixed_result = detect_emotion("I'm WoRrIeD")
        assert lower_result.emotion == upper_result.emotion == mixed_result.emotion
