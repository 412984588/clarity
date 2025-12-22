/**
 * Animated gradient background component
 * Changes color based on detected emotion with smooth 300ms transition
 */

import { LinearGradient } from 'expo-linear-gradient';
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Animated, StyleSheet, ViewStyle } from 'react-native';

import type { EmotionType } from '../types/solve';
import { EMOTION_COLORS } from '../types/solve';

interface AnimatedGradientBackgroundProps {
  emotion: EmotionType;
  enabled: boolean;
  children: React.ReactNode;
  style?: ViewStyle;
}

// Fallback color when disabled
const DISABLED_COLORS: [string, string] = ['#f8fafc', '#f8fafc'];

export const AnimatedGradientBackground: React.FC<AnimatedGradientBackgroundProps> = ({
  emotion,
  enabled,
  children,
  style,
}) => {
  const [fadeAnim] = useState(() => new Animated.Value(1));
  const prevEmotionRef = useRef<EmotionType>(emotion);
  const [key, setKey] = useState(0);

  // Store prev colors before emotion changes
  const prevColors = useMemo(() => {
    return enabled ? EMOTION_COLORS[prevEmotionRef.current] : DISABLED_COLORS;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, key]);

  const colors = useMemo(() => {
    return enabled ? EMOTION_COLORS[emotion] : DISABLED_COLORS;
  }, [enabled, emotion]);

  useEffect(() => {
    if (emotion !== prevEmotionRef.current) {
      // Animate from 0 to 1
      fadeAnim.setValue(0);
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }).start(() => {
        prevEmotionRef.current = emotion;
        setKey((k) => k + 1);
      });
    }
  }, [emotion, fadeAnim]);

  return (
    <Animated.View style={[styles.container, style]}>
      {/* Base gradient layer (previous color) */}
      <LinearGradient
        colors={prevColors}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={StyleSheet.absoluteFillObject}
      />
      {/* Animated overlay gradient (new color) */}
      <Animated.View style={[StyleSheet.absoluteFillObject, { opacity: fadeAnim }]}>
        <LinearGradient
          colors={colors}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={StyleSheet.absoluteFillObject}
        />
      </Animated.View>
      {/* Content */}
      {children}
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default AnimatedGradientBackground;
