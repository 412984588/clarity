# Epic 6: Task Checklist

## Backend Tasks

- [ ] **B1**: Create `app/services/emotion_detector.py`
  - Define `EmotionType` enum (anxious, sad, calm, confused, neutral)
  - Define `EmotionResult` dataclass (emotion: EmotionType, confidence: float)
  - Implement `detect_emotion(text: str) -> EmotionResult`
  - Keyword scoring with weighted matches

- [ ] **B2**: Create `tests/test_emotion_detector.py`
  - Test each emotion detection
  - Test confidence scoring
  - Test neutral fallback

- [ ] **B3**: Update `app/routers/sessions.py`
  - Import emotion_detector
  - Call detect_emotion on user message
  - Add emotion_detected and confidence to SSE done payload

- [ ] **B4**: Run backend checks
  - `poetry run ruff check .`
  - `poetry run mypy app`
  - `poetry run pytest -v`

## Mobile Tasks

- [ ] **M1**: Update `types/solve.ts`
  - Add EmotionType type
  - Update StreamDoneEvent with confidence field

- [ ] **M2**: Create `hooks/useEmotionBackground.ts`
  - AsyncStorage key: `@clarity/emotion_background_enabled`
  - State: currentEmotion, isEnabled
  - Animated value for background
  - 300ms timing animation

- [ ] **M3**: Create `components/AnimatedGradientBackground.tsx`
  - Emotion color mapping
  - LinearGradient with animated colors
  - Props: emotion, enabled, children

- [ ] **M4**: Update `app/session/[id].tsx`
  - Import and use AnimatedGradientBackground
  - Update emotion on SSE done event
  - Respect settings toggle

- [ ] **M5**: Update `app/(tabs)/settings.tsx`
  - Add Preferences card
  - Add emotion background toggle switch
  - Read/write AsyncStorage

- [ ] **M6**: Add i18n keys
  - `settings.preferences`
  - `settings.emotionBackground`
  - `settings.emotionBackgroundDesc`

- [ ] **M7**: Run mobile checks
  - `npm run lint`
  - `npx tsc --noEmit`

## PR Tasks

- [ ] **P1**: Commit all changes
- [ ] **P2**: Push branch
- [ ] **P3**: Create PR via `gh pr create`
- [ ] **P4**: Enable auto-merge via `gh pr merge --auto --squash --delete-branch`
- [ ] **P5**: Return to main and pull

## Verification Matrix

| Check | Command | Expected |
|-------|---------|----------|
| Backend Lint | `poetry run ruff check .` | All checks passed |
| Backend Types | `poetry run mypy app` | Success: no issues |
| Backend Tests | `poetry run pytest -v` | All passed |
| Mobile Lint | `npm run lint` | No errors |
| Mobile Types | `npx tsc --noEmit` | No errors |
