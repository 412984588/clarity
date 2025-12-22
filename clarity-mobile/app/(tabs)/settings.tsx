import { Link } from 'expo-router';
import React, { useCallback, useState } from 'react';
import { Linking, Platform, Pressable, StyleSheet, Text, View } from 'react-native';

import { configureRevenueCat, loginRevenueCat, restorePurchases } from '../../services/revenuecat';
import { useAuth } from '../../stores/authStore';

const SettingsScreen: React.FC = () => {
  const { user, logout, isLoading, getUserId } = useAuth();
  const [billingError, setBillingError] = useState<string | null>(null);

  const ensureRevenueCatReady = useCallback(async () => {
    // 确保 RevenueCat 已初始化并绑定当前用户
    await configureRevenueCat();
    const userId = getUserId();
    if (!userId) {
      throw new Error('缺少用户 ID，请重新登录');
    }
    await loginRevenueCat(userId);
  }, [getUserId]);

  const handleManageSubscription = useCallback(async () => {
    setBillingError(null);
    try {
      const url =
        Platform.OS === 'ios'
          ? 'https://apps.apple.com/account/subscriptions'
          : 'https://play.google.com/store/account/subscriptions';
      const supported = await Linking.canOpenURL(url);
      if (!supported) {
        throw new Error('无法打开订阅管理页面');
      }
      await Linking.openURL(url);
    } catch (_err) {
      setBillingError('打开订阅管理失败，请稍后重试。');
    }
  }, []);

  const handleRestorePurchases = useCallback(async () => {
    setBillingError(null);
    try {
      await ensureRevenueCatReady();
      await restorePurchases();
    } catch (_err) {
      setBillingError('恢复购买失败，请稍后重试。');
    }
  }, [ensureRevenueCatReady]);

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Account</Text>
        <Text style={styles.label}>Signed in as</Text>
        <Text style={styles.email}>{user?.email ?? 'Unknown user'}</Text>

        <Pressable
          onPress={logout}
          style={[styles.logoutButton, isLoading && styles.disabledButton]}
          disabled={isLoading}
        >
          <Text style={styles.logoutText}>Log out</Text>
        </Pressable>
      </View>

      <View style={styles.card}>
        <Text style={styles.title}>Security</Text>
        <Link href="/(tabs)/devices" style={styles.linkRow}>
          Manage Devices
        </Link>
        <Link href="/(tabs)/sessions" style={styles.linkRow}>
          Active Sessions
        </Link>
      </View>

      <View style={styles.card}>
        <Text style={styles.title}>Subscription</Text>
        <Pressable
          onPress={handleManageSubscription}
          style={[styles.actionButton, isLoading && styles.disabledButton]}
          disabled={isLoading}
        >
          <Text style={styles.actionButtonText}>Manage Subscription</Text>
        </Pressable>
        <Pressable
          onPress={handleRestorePurchases}
          style={[styles.actionButton, isLoading && styles.disabledButton]}
          disabled={isLoading}
        >
          <Text style={styles.actionButtonText}>Restore Purchases</Text>
        </Pressable>
        {billingError && <Text style={styles.errorText}>{billingError}</Text>}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f8fafc',
    gap: 16,
  },
  card: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 16,
    shadowColor: '#0f172a',
    shadowOpacity: 0.06,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 6 },
    elevation: 2,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 12,
  },
  label: {
    fontSize: 13,
    color: '#94a3b8',
  },
  email: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    marginTop: 4,
  },
  logoutButton: {
    marginTop: 16,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: '#fee2e2',
    alignItems: 'center',
  },
  logoutText: {
    color: '#b91c1c',
    fontWeight: '600',
  },
  linkRow: {
    paddingVertical: 12,
    color: '#1d4ed8',
    fontWeight: '600',
  },
  actionButton: {
    marginTop: 12,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: '#e2e8f0',
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#1e293b',
    fontWeight: '600',
  },
  disabledButton: {
    opacity: 0.6,
  },
  errorText: {
    color: '#dc2626',
    marginTop: 12,
  },
});

export default SettingsScreen;
