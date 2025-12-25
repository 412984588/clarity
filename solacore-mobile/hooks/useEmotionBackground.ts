/**
 * Hook for managing emotion-based background colors
 * with AsyncStorage persistence and smooth animations
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { useCallback, useEffect, useState } from 'react';
import { Animated } from 'react-native';

import type { EmotionType } from '../types/solve';
import { EMOTION_COLORS } from '../types/solve';

const STORAGE_KEY = '@solacore/emotion_background_enabled';

interface UseEmotionBackgroundResult {
  // Current emotion being displayed
  currentEmotion: EmotionType;
  // Whether the feature is enabled
  isEnabled: boolean;
  // Toggle the feature on/off
  toggleEnabled: () => Promise<void>;
  // Update the current emotion (triggers animation)
  setEmotion: (emotion: EmotionType) => void;
  // Animated value for interpolation (0-1)
  animatedValue: Animated.Value;
  // Current colors based on emotion
  colors: [string, string];
}

export const useEmotionBackground = (): UseEmotionBackgroundResult => {
  const [isEnabled, setIsEnabled] = useState(true);
  const [currentEmotion, setCurrentEmotion] = useState<EmotionType>('neutral');
  const [animatedValue] = useState(() => new Animated.Value(0));

  // Load preference from AsyncStorage on mount
  useEffect(() => {
    const loadPreference = async () => {
      try {
        const stored = await AsyncStorage.getItem(STORAGE_KEY);
        if (stored !== null) {
          setIsEnabled(stored === 'true');
        }
      } catch {
        // Default to enabled if read fails
      }
    };
    void loadPreference();
  }, []);

  // Toggle enabled state
  const toggleEnabled = useCallback(async () => {
    const newValue = !isEnabled;
    setIsEnabled(newValue);
    try {
      await AsyncStorage.setItem(STORAGE_KEY, String(newValue));
    } catch {
      // Ignore storage errors
    }
  }, [isEnabled]);

  // Update emotion with animation
  const setEmotion = useCallback(
    (emotion: EmotionType) => {
      if (emotion === currentEmotion) return;
      setCurrentEmotion(emotion);

      // Reset and animate
      animatedValue.setValue(0);
      Animated.timing(animatedValue, {
        toValue: 1,
        duration: 300,
        useNativeDriver: false,
      }).start();
    },
    [currentEmotion, animatedValue]
  );

  // Get current colors
  const colors = EMOTION_COLORS[currentEmotion];

  return {
    currentEmotion,
    isEnabled,
    toggleEnabled,
    setEmotion,
    animatedValue,
    colors,
  };
};
