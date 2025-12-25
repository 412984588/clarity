import * as Sentry from '@sentry/react-native';
import { Slot, useRouter, useSegments } from 'expo-router';
import React, { useEffect } from 'react';
import { ActivityIndicator, StyleSheet, View } from 'react-native';

import { ErrorBoundary } from '../components/ErrorBoundary';
import { initDatabase } from '../services/database';
import { AuthProvider, useAuth } from '../stores/authStore';

// 初始化 Sentry（仅在生产环境且有 DSN 时）
const sentryDsn = process.env.EXPO_PUBLIC_SENTRY_DSN;
if (sentryDsn) {
  Sentry.init({
    dsn: sentryDsn,
    environment: __DEV__ ? 'development' : 'production',
    tracesSampleRate: 0.1,
    debug: __DEV__,
  });
}

// 初始化 SQLite 数据库（app 启动时只执行一次）
initDatabase().catch((error) => {
  console.error('Failed to initialize database:', error);
  // 报告到 Sentry（如果已初始化）
  if (sentryDsn) {
    Sentry.captureException(error);
  }
});

const AuthGate: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) {
      return;
    }

    const inAuthGroup = segments[0] === '(auth)';

    if (!isAuthenticated && !inAuthGroup) {
      router.replace('/login');
    } else if (isAuthenticated && inAuthGroup) {
      router.replace('/(tabs)/home');
    }
  }, [isAuthenticated, isLoading, router, segments]);

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1d4ed8" />
      </View>
    );
  }

  return <Slot />;
};

const RootLayout: React.FC = () => (
  <ErrorBoundary>
    <AuthProvider>
      <AuthGate />
    </AuthProvider>
  </ErrorBoundary>
);

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f8fafc',
  },
});

export default RootLayout;
