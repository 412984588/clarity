const DEV_API_URL = 'http://localhost:8000';

const resolveApiUrl = (): string => {
  const apiUrl = process.env.EXPO_PUBLIC_API_URL ?? (__DEV__ ? DEV_API_URL : '');
  if (!apiUrl) {
    throw new Error('EXPO_PUBLIC_API_URL is required for production builds');
  }
  return apiUrl;
};

export const API_URL = resolveApiUrl();
export const REVENUECAT_API_KEY_IOS = process.env.EXPO_PUBLIC_REVENUECAT_API_KEY_IOS ?? '';
export const REVENUECAT_API_KEY_ANDROID =
  process.env.EXPO_PUBLIC_REVENUECAT_API_KEY_ANDROID ?? '';

// Free Beta 模式配置
export const BETA_MODE = process.env.EXPO_PUBLIC_BETA_MODE === 'true';
export const BILLING_ENABLED = process.env.EXPO_PUBLIC_BILLING_ENABLED !== 'false';
