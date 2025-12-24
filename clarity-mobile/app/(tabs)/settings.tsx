import { Link } from 'expo-router';
import React, { useCallback, useState } from 'react';
import { Alert, Linking, Platform, Pressable, Share, StyleSheet, Switch, Text, View } from 'react-native';
import RevenueCatUI from 'react-native-purchases-ui';

import { useEmotionBackground } from '../../hooks/useEmotionBackground';
import { t } from '../../i18n';
import { deleteAccount, exportAccountData } from '../../services/account';
import { BETA_MODE, BILLING_ENABLED } from '../../services/config';
import { configureRevenueCat, loginRevenueCat, restorePurchases } from '../../services/revenuecat';
import { useAuth } from '../../stores/authStore';

const SettingsScreen: React.FC = () => {
  const { user, logout, isLoading, getUserId } = useAuth();
  const [billingError, setBillingError] = useState<string | null>(null);
  const [accountError, setAccountError] = useState<string | null>(null);
  const [accountBusy, setAccountBusy] = useState(false);
  const { isEnabled: emotionBackgroundEnabled, toggleEnabled: toggleEmotionBackground } =
    useEmotionBackground();

  const ensureRevenueCatReady = useCallback(async () => {
    await configureRevenueCat();
    const userId = getUserId();
    if (!userId) {
      throw new Error(t('settings.missingUserId'));
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
        throw new Error(t('settings.openSubscriptionFailed'));
      }
      await Linking.openURL(url);
    } catch (_err) {
      setBillingError(t('settings.openSubscriptionFailed'));
    }
  }, []);

  const handleRestorePurchases = useCallback(async () => {
    setBillingError(null);
    try {
      await ensureRevenueCatReady();
      await restorePurchases();
    } catch (_err) {
      setBillingError(t('settings.restorePurchasesFailed'));
    }
  }, [ensureRevenueCatReady]);

  const handleCustomerCenter = useCallback(async () => {
    setBillingError(null);
    try {
      await ensureRevenueCatReady();
      await RevenueCatUI.presentCustomerCenter();
    } catch (_err) {
      setBillingError(t('settings.customerCenterFailed'));
    }
  }, [ensureRevenueCatReady]);

  const handleExportData = useCallback(async () => {
    setAccountError(null);
    setAccountBusy(true);
    try {
      const data = await exportAccountData();
      const payload = JSON.stringify(data, null, 2);
      await Share.share({
        title: t('settings.exportShareTitle'),
        message: payload,
      });
    } catch (_err) {
      setAccountError(t('settings.exportFailed'));
    } finally {
      setAccountBusy(false);
    }
  }, []);

  const handleDeleteAccount = useCallback(async () => {
    setAccountError(null);
    setAccountBusy(true);
    try {
      await deleteAccount();
      await logout();
      Alert.alert(t('settings.deleteAccountSuccess'));
    } catch (_err) {
      setAccountError(t('settings.deleteAccountFailed'));
    } finally {
      setAccountBusy(false);
    }
  }, [logout]);

  const confirmDeleteAccount = useCallback(() => {
    Alert.alert(
      t('settings.deleteAccountConfirmTitle'),
      t('settings.deleteAccountConfirmBody'),
      [
        { text: t('common.cancel'), style: 'cancel' },
        {
          text: t('settings.deleteAccountConfirmAction'),
          style: 'destructive',
          onPress: handleDeleteAccount,
        },
      ]
    );
  }, [handleDeleteAccount]);

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>{t('settings.title')}</Text>
        <Text style={styles.label}>{t('settings.signedInAs')}</Text>
        <Text style={styles.email}>{user?.email ?? t('common.unknownUser')}</Text>

        <Pressable
          onPress={logout}
          style={[styles.logoutButton, isLoading && styles.disabledButton]}
          disabled={isLoading}
        >
          <Text style={styles.logoutText}>{t('common.logout')}</Text>
        </Pressable>
      </View>

      <View style={styles.card}>
        <Text style={styles.title}>{t('settings.security')}</Text>
        <Link href="/(tabs)/devices" style={styles.linkRow}>
          {t('settings.manageDevices')}
        </Link>
        <Link href="/(tabs)/sessions" style={styles.linkRow}>
          {t('settings.activeSessions')}
        </Link>
      </View>

      <View style={styles.card}>
        <Text style={styles.title}>{t('settings.preferences')}</Text>
        <View style={styles.toggleRow}>
          <View style={styles.toggleTextContainer}>
            <Text style={styles.toggleLabel}>{t('settings.emotionBackground')}</Text>
            <Text style={styles.toggleDesc}>{t('settings.emotionBackgroundDesc')}</Text>
          </View>
          <Switch
            value={emotionBackgroundEnabled}
            onValueChange={toggleEmotionBackground}
            trackColor={{ false: '#e2e8f0', true: '#bfdbfe' }}
            thumbColor={emotionBackgroundEnabled ? '#1d4ed8' : '#f4f4f5'}
          />
        </View>
      </View>

      {BETA_MODE && (
        <View style={styles.card}>
          <Text style={styles.title}>{t('settings.betaMode')}</Text>
          <Text style={styles.betaText}>{t('settings.betaModeDesc')}</Text>
        </View>
      )}

      {BILLING_ENABLED && (
        <View style={styles.card}>
          <Text style={styles.title}>{t('settings.subscription')}</Text>
        <Pressable
          onPress={handleManageSubscription}
          style={[styles.actionButton, (isLoading || accountBusy) && styles.disabledButton]}
          disabled={isLoading || accountBusy}
        >
          <Text style={styles.actionButtonText}>{t('settings.manageSubscription')}</Text>
        </Pressable>
        <Pressable
          onPress={handleRestorePurchases}
          style={[styles.actionButton, (isLoading || accountBusy) && styles.disabledButton]}
          disabled={isLoading || accountBusy}
        >
          <Text style={styles.actionButtonText}>{t('settings.restorePurchases')}</Text>
        </Pressable>
        <Pressable
          onPress={handleCustomerCenter}
          style={[styles.actionButton, (isLoading || accountBusy) && styles.disabledButton]}
          disabled={isLoading || accountBusy}
        >
          <Text style={styles.actionButtonText}>{t('settings.customerCenter')}</Text>
        </Pressable>
        {billingError && <Text style={styles.errorText}>{billingError}</Text>}
        </View>
      )}

      <View style={styles.card}>
        <Text style={styles.title}>{t('settings.dataPrivacy')}</Text>
        <Pressable
          onPress={handleExportData}
          style={[styles.actionButton, (isLoading || accountBusy) && styles.disabledButton]}
          disabled={isLoading || accountBusy}
        >
          <Text style={styles.actionButtonText}>{t('settings.exportData')}</Text>
        </Pressable>
        <Pressable
          onPress={confirmDeleteAccount}
          style={[styles.dangerButton, (isLoading || accountBusy) && styles.disabledButton]}
          disabled={isLoading || accountBusy}
        >
          <Text style={styles.dangerButtonText}>{t('settings.deleteAccount')}</Text>
        </Pressable>
        {accountError && <Text style={styles.errorText}>{accountError}</Text>}
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
  dangerButton: {
    marginTop: 12,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: '#fee2e2',
    alignItems: 'center',
  },
  dangerButtonText: {
    color: '#b91c1c',
    fontWeight: '600',
  },
  disabledButton: {
    opacity: 0.6,
  },
  errorText: {
    color: '#dc2626',
    marginTop: 12,
  },
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  toggleTextContainer: {
    flex: 1,
    marginRight: 12,
  },
  toggleLabel: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1e293b',
  },
  toggleDesc: {
    fontSize: 13,
    color: '#64748b',
    marginTop: 2,
  },
  betaText: {
    fontSize: 14,
    color: '#64748b',
    lineHeight: 20,
  },
});

export default SettingsScreen;
