import type { PurchasesOfferings, PurchasesPackage } from 'react-native-purchases';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { t } from '../../i18n';
import {
  configureRevenueCat,
  getOfferings,
  loginRevenueCat,
  purchasePackage,
  restorePurchases,
} from '../../services/revenuecat';
import { useAuth } from '../../stores/authStore';

const PaywallScreen: React.FC = () => {
  const { getUserId } = useAuth();
  const [offerings, setOfferings] = useState<PurchasesOfferings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPurchasing, setIsPurchasing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const userId = getUserId();

  const loadOfferings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setNotice(null);

    try {
      // 初始化 RevenueCat 并绑定当前用户
      await configureRevenueCat();
      if (userId) {
        await loginRevenueCat(userId);
      } else {
        throw new Error(t('paywall.missingUserId'));
      }

      const data = await getOfferings();
      setOfferings(data);
    } catch (_err) {
      setError(t('paywall.loadFailed'));
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    void loadOfferings();
  }, [loadOfferings]);

  const availablePackages = useMemo(
    () => offerings?.current?.availablePackages ?? [],
    [offerings]
  );

  const handlePurchase = useCallback(async (packageToPurchase: PurchasesPackage) => {
    setIsPurchasing(true);
    setError(null);
    setNotice(null);

    try {
      await purchasePackage(packageToPurchase);
      setNotice(t('paywall.purchaseSuccess'));
    } catch (_err) {
      setError(t('paywall.purchaseFailed'));
    } finally {
      setIsPurchasing(false);
    }
  }, []);

  const handleRestore = useCallback(async () => {
    setIsPurchasing(true);
    setError(null);
    setNotice(null);

    try {
      await restorePurchases();
      setNotice(t('paywall.restoreSuccess'));
    } catch (_err) {
      setError(t('settings.restorePurchasesFailed'));
    } finally {
      setIsPurchasing(false);
    }
  }, []);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{t('paywall.title')}</Text>
      <Text style={styles.subtitle}>{t('paywall.subtitle')}</Text>

      {isLoading ? (
        <ActivityIndicator style={styles.loader} color="#1d4ed8" />
      ) : (
        <View style={styles.list}>
          {availablePackages.map((pkg) => (
            <View key={pkg.identifier} style={styles.card}>
              <Text style={styles.packageTitle}>{pkg.product.title}</Text>
              <Text style={styles.packagePrice}>{pkg.product.priceString}</Text>
              <Text style={styles.packageDescription}>
                {pkg.product.description || 'Best for power users.'}
              </Text>

              <Pressable
                onPress={() => handlePurchase(pkg)}
                style={[styles.primaryButton, isPurchasing && styles.disabledButton]}
                disabled={isPurchasing}
              >
                <Text style={styles.primaryButtonText}>{t('paywall.purchase')}</Text>
              </Pressable>
            </View>
          ))}

          {availablePackages.length === 0 && (
            <Text style={styles.emptyText}>{t('paywall.noPackages')}</Text>
          )}
        </View>
      )}

      <Pressable
        onPress={handleRestore}
        style={[styles.secondaryButton, isPurchasing && styles.disabledButton]}
        disabled={isPurchasing}
      >
        <Text style={styles.secondaryButtonText}>{t('settings.restorePurchases')}</Text>
      </Pressable>

      {notice && <Text style={styles.noticeText}>{notice}</Text>}
      {error && <Text style={styles.errorText}>{error}</Text>}
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
  title: {
    fontSize: 22,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 6,
  },
  subtitle: {
    color: '#64748b',
    marginBottom: 16,
  },
  list: {
    gap: 16,
  },
  card: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 16,
    shadowColor: '#0f172a',
    shadowOpacity: 0.06,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 6 },
    elevation: 2,
  },
  packageTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
  },
  packagePrice: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1d4ed8',
    marginTop: 6,
  },
  packageDescription: {
    color: '#64748b',
    marginTop: 6,
  },
  primaryButton: {
    marginTop: 14,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: '#1d4ed8',
    alignItems: 'center',
  },
  primaryButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  secondaryButton: {
    marginTop: 20,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: '#e2e8f0',
    alignItems: 'center',
  },
  secondaryButtonText: {
    color: '#1e293b',
    fontWeight: '600',
  },
  disabledButton: {
    opacity: 0.6,
  },
  emptyText: {
    color: '#94a3b8',
    textAlign: 'center',
    marginTop: 12,
  },
  errorText: {
    color: '#dc2626',
    marginTop: 16,
  },
  noticeText: {
    color: '#15803d',
    marginTop: 16,
  },
  loader: {
    marginTop: 30,
  },
});

export default PaywallScreen;
