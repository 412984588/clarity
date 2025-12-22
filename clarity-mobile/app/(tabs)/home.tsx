import { useRouter } from 'expo-router';
import React, { useCallback, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { t } from '../../i18n';
import { useAuth } from '../../stores/authStore';

const HomeScreen: React.FC = () => {
  const router = useRouter();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const handleStartSession = useCallback(() => {
    setIsLoading(true);
    // Navigate to new session (id='new' triggers creation)
    router.push('/session/new');
    // Reset loading after a short delay
    setTimeout(() => setIsLoading(false), 500);
  }, [router]);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Welcome Section */}
      <View style={styles.welcomeSection}>
        <Text style={styles.greeting}>{t('home.greeting')}</Text>
        <Text style={styles.userName}>{user?.email ?? t('common.unknownUser')}</Text>
      </View>

      {/* Start Session Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>{t('home.solveTitle')}</Text>
        <Text style={styles.cardDescription}>{t('home.solveDescription')}</Text>

        <View style={styles.stepsPreview}>
          <View style={styles.stepPreviewItem}>
            <Text style={styles.stepPreviewNumber}>1</Text>
            <Text style={styles.stepPreviewLabel}>{t('solve.stepReceive')}</Text>
          </View>
          <Text style={styles.stepPreviewArrow}>→</Text>
          <View style={styles.stepPreviewItem}>
            <Text style={styles.stepPreviewNumber}>2</Text>
            <Text style={styles.stepPreviewLabel}>{t('solve.stepClarify')}</Text>
          </View>
          <Text style={styles.stepPreviewArrow}>→</Text>
          <View style={styles.stepPreviewItem}>
            <Text style={styles.stepPreviewNumber}>3</Text>
            <Text style={styles.stepPreviewLabel}>{t('solve.stepReframe')}</Text>
          </View>
          <Text style={styles.stepPreviewArrow}>→</Text>
          <View style={styles.stepPreviewItem}>
            <Text style={styles.stepPreviewNumber}>4</Text>
            <Text style={styles.stepPreviewLabel}>{t('solve.stepOptions')}</Text>
          </View>
          <Text style={styles.stepPreviewArrow}>→</Text>
          <View style={styles.stepPreviewItem}>
            <Text style={styles.stepPreviewNumber}>5</Text>
            <Text style={styles.stepPreviewLabel}>{t('solve.stepCommit')}</Text>
          </View>
        </View>

        <Pressable
          style={[styles.startButton, isLoading && styles.startButtonDisabled]}
          onPress={handleStartSession}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.startButtonText}>{t('home.startSession')}</Text>
          )}
        </Pressable>
      </View>

      {/* Info Section */}
      <View style={styles.infoSection}>
        <Text style={styles.infoTitle}>{t('home.howItWorks')}</Text>
        <View style={styles.infoItem}>
          <Text style={styles.infoIcon}>💬</Text>
          <View style={styles.infoContent}>
            <Text style={styles.infoHeading}>{t('home.step1Title')}</Text>
            <Text style={styles.infoText}>{t('home.step1Desc')}</Text>
          </View>
        </View>
        <View style={styles.infoItem}>
          <Text style={styles.infoIcon}>🎯</Text>
          <View style={styles.infoContent}>
            <Text style={styles.infoHeading}>{t('home.step2Title')}</Text>
            <Text style={styles.infoText}>{t('home.step2Desc')}</Text>
          </View>
        </View>
        <View style={styles.infoItem}>
          <Text style={styles.infoIcon}>✅</Text>
          <View style={styles.infoContent}>
            <Text style={styles.infoHeading}>{t('home.step3Title')}</Text>
            <Text style={styles.infoText}>{t('home.step3Desc')}</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },

  // Welcome
  welcomeSection: {
    marginBottom: 24,
  },
  greeting: {
    fontSize: 16,
    color: '#64748b',
  },
  userName: {
    fontSize: 24,
    fontWeight: '700',
    color: '#0f172a',
    marginTop: 4,
  },

  // Card
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#0f172a',
    shadowOpacity: 0.08,
    shadowRadius: 16,
    shadowOffset: { width: 0, height: 8 },
    elevation: 3,
    marginBottom: 24,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 8,
  },
  cardDescription: {
    fontSize: 14,
    color: '#64748b',
    lineHeight: 20,
    marginBottom: 20,
  },

  // Steps Preview
  stepsPreview: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    flexWrap: 'wrap',
    marginBottom: 20,
    gap: 4,
  },
  stepPreviewItem: {
    alignItems: 'center',
    width: 48,
  },
  stepPreviewNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#e0e7ff',
    color: '#1d4ed8',
    fontSize: 12,
    fontWeight: '700',
    textAlign: 'center',
    lineHeight: 24,
  },
  stepPreviewLabel: {
    fontSize: 9,
    color: '#64748b',
    marginTop: 4,
    textAlign: 'center',
  },
  stepPreviewArrow: {
    color: '#cbd5e1',
    fontSize: 12,
  },

  // Start Button
  startButton: {
    backgroundColor: '#1d4ed8',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  startButtonDisabled: {
    opacity: 0.6,
  },
  startButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },

  // Info Section
  infoSection: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 16,
  },
  infoItem: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  infoIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  infoContent: {
    flex: 1,
  },
  infoHeading: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0f172a',
    marginBottom: 2,
  },
  infoText: {
    fontSize: 13,
    color: '#64748b',
    lineHeight: 18,
  },
});

export default HomeScreen;
