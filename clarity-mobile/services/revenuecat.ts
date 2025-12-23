import Purchases, { CustomerInfo, PurchasesOfferings, PurchasesPackage } from 'react-native-purchases';
import { Platform } from 'react-native';

import { REVENUECAT_API_KEY_ANDROID, REVENUECAT_API_KEY_IOS } from './config';

export const configureRevenueCat = async (): Promise<void> => {
  try {
    const apiKey = Platform.OS === 'ios' ? REVENUECAT_API_KEY_IOS : REVENUECAT_API_KEY_ANDROID;
    if (!apiKey) {
      throw new Error('RevenueCat API Key 未配置');
    }
    // 初始化 RevenueCat SDK
    Purchases.configure({ apiKey });
  } catch (error) {
    // 记录错误，便于排查配置问题
    console.error('RevenueCat 配置失败', error);
    throw error;
  }
};

export const loginRevenueCat = async (userId: string): Promise<void> => {
  try {
    if (!userId) {
      throw new Error('userId 为空，无法登录 RevenueCat');
    }
    await Purchases.logIn(userId);
  } catch (error) {
    console.error('RevenueCat 登录失败', error);
    throw error;
  }
};

export const logoutRevenueCat = async (): Promise<void> => {
  try {
    await Purchases.logOut();
  } catch (error) {
    console.error('RevenueCat 登出失败', error);
    throw error;
  }
};

export const getOfferings = async (): Promise<PurchasesOfferings | null> => {
  try {
    const offerings = await Purchases.getOfferings();
    return offerings;
  } catch (error) {
    console.error('获取 RevenueCat Offerings 失败', error);
    throw error;
  }
};

export const purchasePackage = async (packageToPurchase: PurchasesPackage): Promise<CustomerInfo> => {
  try {
    const { customerInfo } = await Purchases.purchasePackage(packageToPurchase);
    return customerInfo;
  } catch (error) {
    console.error('RevenueCat 购买失败', error);
    throw error;
  }
};

export const restorePurchases = async (): Promise<CustomerInfo> => {
  try {
    const customerInfo = await Purchases.restorePurchases();
    return customerInfo;
  } catch (error) {
    console.error('RevenueCat 恢复购买失败', error);
    throw error;
  }
};
