import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { apiRequest, refreshTokens, type ApiError } from '../services/api';
import {
  clearTokens,
  clearUserEmail,
  clearUserId,
  getDeviceFingerprint,
  getTokens,
  getUserEmail,
  getUserId as getStoredUserId,
  saveTokens,
  saveUserEmail,
  saveUserId,
} from '../services/auth';

type User = {
  id?: string;
  email?: string;
};

type AuthContextValue = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  setSession: (
    accessToken: string,
    refreshToken: string,
    email?: string | null,
    userId?: string | null
  ) => Promise<void>;
  getUserId: () => string | null;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const getErrorMessage = (error: unknown): string => {
  if (typeof error === 'string') {
    return error;
  }

  if (error && typeof error === 'object') {
    const apiError = error as ApiError;
    if (apiError.message) {
      return apiError.message;
    }
    if ('message' in apiError && typeof apiError.message === 'string') {
      return apiError.message;
    }
  }

  return 'Something went wrong. Please try again.';
};

export const AuthProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const initialize = useCallback(async () => {
    setIsLoading(true);
    try {
      const tokens = await getTokens();
      if (tokens.refreshToken) {
        await refreshTokens();
        const [email, userId] = await Promise.all([getUserEmail(), getStoredUserId()]);
        if (email || userId) {
          setUser({ email: email ?? undefined, id: userId ?? undefined });
        }
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }
    } catch {
      await clearTokens();
      await clearUserEmail();
      await clearUserId();
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void initialize();
  }, [initialize]);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const deviceFingerprint = await getDeviceFingerprint();
      const response = await apiRequest<{
        access_token: string;
        refresh_token: string;
        user_id?: string | null;
      }>('/auth/login', {
        method: 'POST',
        auth: false,
        body: { email, password, device_fingerprint: deviceFingerprint },
      });
      await saveTokens(response.access_token, response.refresh_token);
      await saveUserEmail(email);
      if (response.user_id) {
        await saveUserId(response.user_id);
      }
      setUser({ email, id: response.user_id ?? undefined });
      setIsAuthenticated(true);
    } catch (err) {
      setError(getErrorMessage(err));
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const deviceFingerprint = await getDeviceFingerprint();
      const response = await apiRequest<{
        access_token: string;
        refresh_token: string;
        user_id?: string | null;
      }>('/auth/register', {
        method: 'POST',
        auth: false,
        body: { email, password, device_fingerprint: deviceFingerprint },
      });
      await saveTokens(response.access_token, response.refresh_token);
      await saveUserEmail(email);
      if (response.user_id) {
        await saveUserId(response.user_id);
      }
      setUser({ email, id: response.user_id ?? undefined });
      setIsAuthenticated(true);
    } catch (err) {
      setError(getErrorMessage(err));
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await apiRequest('/auth/logout', { method: 'POST' });
    } catch {
      // Ignore logout errors, still clear local session
    }
    await clearTokens();
    await clearUserEmail();
    await clearUserId();
    setUser(null);
    setIsAuthenticated(false);
    setIsLoading(false);
  }, []);

  const refreshToken = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      await refreshTokens();
      const [email, userId] = await Promise.all([getUserEmail(), getStoredUserId()]);
      if (email || userId) {
        setUser({ email: email ?? undefined, id: userId ?? undefined });
      }
      setIsAuthenticated(true);
    } catch (err) {
      setError(getErrorMessage(err));
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const setSession = useCallback(
    async (
      accessToken: string,
      refreshTokenValue: string,
      email?: string | null,
      userId?: string | null
    ) => {
      setIsLoading(true);
      setError(null);
      await saveTokens(accessToken, refreshTokenValue);
      if (email) {
        await saveUserEmail(email);
        setUser({ email, id: userId ?? undefined });
      } else if (userId) {
        setUser({ id: userId });
      }
      if (userId) {
        await saveUserId(userId);
      }
      setIsAuthenticated(true);
      setIsLoading(false);
    },
    []
  );

  const getUserId = useCallback(() => user?.id ?? null, [user]);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated,
      isLoading,
      error,
      login,
      register,
      logout,
      refreshToken,
      setSession,
      getUserId,
    }),
    [
      user,
      isAuthenticated,
      isLoading,
      error,
      login,
      register,
      logout,
      refreshToken,
      setSession,
      getUserId,
    ]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
