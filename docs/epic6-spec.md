# Epic 6: Emotion Detection + UI Effects

## Overview

Add real-time emotion detection to the Solve flow, displaying visual feedback through animated gradient backgrounds that reflect the user's detected emotional state.

## User Story

As a user going through a Solve session, I want to see the app's background subtly change color based on my detected emotional state, so that I feel the app is responsive and empathetic to my mental state.

## Requirements

### Backend

1. **Emotion Detection in SSE Done Event**
   - Endpoint: `POST /sessions/{session_id}/messages`
   - SSE `done` event must include:
     ```json
     {
       "next_step": "clarify",
       "emotion_detected": "anxious",
       "confidence": 0.85
     }
     ```
   - `emotion_detected`: One of `anxious`, `sad`, `calm`, `confused`, `neutral`
   - `confidence`: Float between 0.0 and 1.0

2. **Emotion Detection Logic**
   - Analyze user message content for emotional indicators
   - Keywords/patterns for each emotion:
     - `anxious`: worried, scared, nervous, panic, stress, anxiety, overwhelmed
     - `sad`: sad, depressed, hopeless, crying, lonely, grief, loss
     - `calm`: peaceful, relaxed, content, grateful, happy, optimistic
     - `confused`: confused, unsure, lost, don't understand, unclear
     - `neutral`: default when no strong signals detected
   - Return highest confidence match

### Mobile

1. **Gradient Background Animation**
   - Apply to Session screen container
   - Emotion color mapping:
     | Emotion | Color Gradient |
     |---------|----------------|
     | anxious | Orange-Red (#ff6b4a → #ff4757) |
     | sad | Blue-Purple (#667eea → #764ba2) |
     | calm | Green (#48c774 → #2ecc71) |
     | confused | Yellow-Orange (#ffa502 → #ff7f50) |
     | neutral | Gray-Blue (#a8b5c8 → #8395a7) |
   - 300ms smooth transition on emotion change
   - Use `Animated` API with `timing` for smooth transitions

2. **Settings Toggle**
   - Add "Emotion Gradient Background" toggle in Settings
   - Default: ON
   - Store preference in AsyncStorage
   - Key: `@clarity/emotion_background_enabled`

3. **i18n**
   - All new strings must be localized (en, es, zh)
   - Keys required:
     - `settings.emotionBackground`
     - `settings.emotionBackgroundDesc`

## Acceptance Criteria

- [ ] Backend SSE done event includes `emotion_detected` and `confidence`
- [ ] Mobile session screen shows gradient background based on emotion
- [ ] Background transitions smoothly over 300ms
- [ ] Settings contains working toggle for emotion background
- [ ] Toggle preference persists across app restarts
- [ ] All tests pass (ruff, mypy, pytest, lint, tsc)
- [ ] All strings are internationalized

## Out of Scope

- Emotion history tracking/analytics
- Custom color preferences
- Haptic feedback on emotion change
