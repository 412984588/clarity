"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import type { User } from "@/lib/types";
import {
  getCurrentUser,
  isAuthenticated,
  logout as clearAuth,
  refreshToken,
} from "@/lib/auth";
import { getStoredTokens } from "@/lib/api";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  error: string | null;
  refreshUser: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshUser = useCallback(async () => {
    setError(null);
    setLoading(true);

    try {
      if (isAuthenticated()) {
        setUser(getCurrentUser());
        return;
      }

      const stored = getStoredTokens();
      if (stored?.refresh_token) {
        await refreshToken();
        setUser(getCurrentUser());
        return;
      }

      setUser(null);
    } catch (err) {
      clearAuth();
      setUser(null);
      setError(
        err instanceof Error ? err.message : "Failed to refresh session",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);

  const logout = useCallback(() => {
    clearAuth();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      error,
      refreshUser,
      logout,
    }),
    [user, loading, error, refreshUser, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
