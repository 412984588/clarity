import * as Crypto from 'expo-crypto';
import * as SecureStore from 'expo-secure-store';

const ACCESS_TOKEN_KEY = 'auth_access_token';
const REFRESH_TOKEN_KEY = 'auth_refresh_token';
const DEVICE_FINGERPRINT_KEY = 'device_fingerprint';
const USER_EMAIL_KEY = 'auth_user_email';

const bytesToHex = (bytes: Uint8Array): string =>
  Array.from(bytes)
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');

export const getDeviceFingerprint = async (): Promise<string> => {
  const existing = await SecureStore.getItemAsync(DEVICE_FINGERPRINT_KEY);
  if (existing) {
    return existing;
  }

  const bytes = await Crypto.getRandomBytesAsync(32);
  const fingerprint = bytesToHex(bytes);
  await SecureStore.setItemAsync(DEVICE_FINGERPRINT_KEY, fingerprint);
  return fingerprint;
};

export const saveTokens = async (accessToken: string, refreshToken: string): Promise<void> => {
  await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, accessToken);
  await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, refreshToken);
};

export const getTokens = async (): Promise<{
  accessToken: string | null;
  refreshToken: string | null;
}> => {
  const [accessToken, refreshToken] = await Promise.all([
    SecureStore.getItemAsync(ACCESS_TOKEN_KEY),
    SecureStore.getItemAsync(REFRESH_TOKEN_KEY),
  ]);

  return { accessToken, refreshToken };
};

export const clearTokens = async (): Promise<void> => {
  await Promise.all([
    SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY),
    SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY),
  ]);
};

export const saveUserEmail = async (email: string): Promise<void> => {
  await SecureStore.setItemAsync(USER_EMAIL_KEY, email);
};

export const getUserEmail = async (): Promise<string | null> =>
  SecureStore.getItemAsync(USER_EMAIL_KEY);

export const clearUserEmail = async (): Promise<void> => {
  await SecureStore.deleteItemAsync(USER_EMAIL_KEY);
};
