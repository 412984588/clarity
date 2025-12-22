# Epic 6: Implementation Plan

## Phase 1: Backend Emotion Detection

### 1.1 Create Emotion Detector Service
- Create `app/services/emotion_detector.py`
- Define `EmotionType` enum: anxious, sad, calm, confused, neutral
- Define `EmotionResult` dataclass with emotion and confidence
- Implement keyword-based detection with weighted scoring

### 1.2 Integrate into SSE Endpoint
- Modify `POST /sessions/{session_id}/messages`
- Call emotion detector on user message
- Include `emotion_detected` and `confidence` in done event payload

### 1.3 Add Tests
- Unit tests for emotion detector
- Integration tests for SSE done event

## Phase 2: Mobile Gradient Background

### 2.1 Create Emotion Context/Hook
- Create `hooks/useEmotionBackground.ts`
- Store current emotion in state
- Provide animated background value
- Handle AsyncStorage for toggle preference

### 2.2 Implement Animated Gradient
- Add emotion color mapping constants
- Create `AnimatedGradientBackground` component
- Use `Animated.timing` with 300ms duration
- Apply `easeInOut` interpolation

### 2.3 Integrate into Session Screen
- Wrap session content with gradient background
- Update emotion on SSE done event
- Only apply when setting enabled

## Phase 3: Settings Toggle

### 3.1 Add Toggle Component
- Add switch to Settings screen
- Read/write AsyncStorage preference
- Use i18n for labels

### 3.2 Connect to Emotion Context
- Create `stores/emotionSettingsStore.ts` or use context
- Provide global access to preference

## Phase 4: i18n & Testing

### 4.1 Add Translations
- Add keys to en.json, es.json, zh.json
- `settings.emotionBackground`
- `settings.emotionBackgroundDesc`

### 4.2 Verification
- Backend: `ruff check .`, `mypy app`, `pytest`
- Mobile: `npm run lint`, `npx tsc --noEmit`

## File Changes Summary

### New Files
- `clarity-api/app/services/emotion_detector.py`
- `clarity-api/tests/test_emotion_detector.py`
- `clarity-mobile/hooks/useEmotionBackground.ts`
- `clarity-mobile/components/AnimatedGradientBackground.tsx`

### Modified Files
- `clarity-api/app/routers/sessions.py`
- `clarity-mobile/app/session/[id].tsx`
- `clarity-mobile/app/(tabs)/settings.tsx`
- `clarity-mobile/types/solve.ts`
- `clarity-mobile/i18n/en.json`
- `clarity-mobile/i18n/es.json`
- `clarity-mobile/i18n/zh.json`
