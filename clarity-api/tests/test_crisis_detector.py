"""Crisis detector tests - verify crisis keyword detection in multiple languages."""

from app.services.crisis_detector import (
    CRISIS_RESOURCES,
    detect_crisis,
    get_crisis_response,
)


class TestCrisisDetector:
    """Test crisis detection functionality."""

    def test_detect_english_suicide_keywords(self):
        """Test detection of English crisis keywords."""
        # 直接关键词
        result = detect_crisis("I want to kill myself")
        assert result.blocked is True
        assert result.reason == "CRISIS"
        assert result.resources == CRISIS_RESOURCES

        result = detect_crisis("thinking about suicide")
        assert result.blocked is True

        result = detect_crisis("I want to end my life")
        assert result.blocked is True

    def test_detect_english_self_harm_keywords(self):
        """Test detection of self-harm keywords."""
        result = detect_crisis("I want to hurt myself")
        assert result.blocked is True

        result = detect_crisis("I've been cutting myself")
        assert result.blocked is True

    def test_detect_spanish_keywords(self):
        """Test detection of Spanish crisis keywords."""
        result = detect_crisis("Quiero matarme")
        assert result.blocked is True
        assert result.reason == "CRISIS"

        result = detect_crisis("pensando en suicidio")
        assert result.blocked is True

        result = detect_crisis("quiero quitarme la vida")
        assert result.blocked is True

    def test_no_crisis_normal_messages(self):
        """Test that normal messages are not flagged."""
        result = detect_crisis("I'm feeling stressed about work")
        assert result.blocked is False

        result = detect_crisis("My relationship is difficult")
        assert result.blocked is False

        result = detect_crisis("I need help with my anxiety")
        assert result.blocked is False

    def test_case_insensitive(self):
        """Test that detection is case insensitive."""
        result = detect_crisis("I WANT TO KILL MYSELF")
        assert result.blocked is True

        result = detect_crisis("Suicide")
        assert result.blocked is True

    def test_get_crisis_response_format(self):
        """Test that crisis response has correct format."""
        response = get_crisis_response()

        assert response["blocked"] is True
        assert response["reason"] == "CRISIS"
        assert "resources" in response
        assert "US" in response["resources"]
        assert "ES" in response["resources"]
        assert response["resources"]["US"] == "988"
        assert response["resources"]["ES"] == "717 003 717"

    def test_crisis_resources_contain_required_hotlines(self):
        """Test that crisis resources include required hotlines."""
        assert CRISIS_RESOURCES["US"] == "988"
        assert CRISIS_RESOURCES["ES"] == "717 003 717"

    def test_matched_keyword_returned(self):
        """Test that the matched keyword is returned in result."""
        result = detect_crisis("I'm thinking about suicide today")
        assert result.blocked is True
        assert result.matched_keyword is not None
        assert "suicide" in result.matched_keyword.lower()
