import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { apiRequest, refreshTokens, type ApiError } from '../services/api';
import {
  clearTokens,
  clearUserEmail,
  getDeviceFingerprint,
  getTokens,
  getUserEmail,
  saveTokens,
  saveUserEmail,
} from '../services/auth';

type User = {
  email: string;
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
  setSession: (accessToken: string, refreshToken: string, email?: string | null) => Promise<void>;
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
        const email = await getUserEmail();
        if (email) {
          setUser({ email });
        }
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }
    } catch {
      await clearTokens();
      await clearUserEmail();
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
      const response = await apiRequest<{ access_token: string; refresh_token: string }>(
        '/auth/login',
        {
          method: 'POST',
          auth: false,
          body: { email, password, device_fingerprint: deviceFingerprint },
        }
      );
      await saveTokens(response.access_token, response.refresh_token);
      await saveUserEmail(email);
      setUser({ email });
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
      const response = await apiRequest<{ access_token: string; refresh_token: string }>(
        '/auth/register',
        {
          method: 'POST',
          auth: false,
          body: { email, password, device_fingerprint: deviceFingerprint },
        }
      );
      await saveTokens(response.access_token, response.refresh_token);
      await saveUserEmail(email);
      setUser({ email });
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
    await clearTokens();
    await clearUserEmail();
    setUser(null);
    setIsAuthenticated(false);
    setIsLoading(false);
  }, []);

  const refreshToken = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      await refreshTokens();
      const email = await getUserEmail();
      if (email) {
        setUser({ email });
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
    async (accessToken: string, refreshTokenValue: string, email?: string | null) => {
      setIsLoading(true);
      setError(null);
      await saveTokens(accessToken, refreshTokenValue);
      if (email) {
        await saveUserEmail(email);
        setUser({ email });
      }
      setIsAuthenticated(true);
      setIsLoading(false);
    },
    []
  );

  const value = useMemo(
    () => ({ user, isAuthenticated, isLoading, error, login, register, logout, refreshToken, setSession }),
    [user, isAuthenticated, isLoading, error, login, register, logout, refreshToken, setSession]
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
