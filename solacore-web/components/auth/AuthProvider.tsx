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
import { getCurrentUser, logout as clearAuth, refreshToken } from "@/lib/auth";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  error: string | null;
  refreshUser: () => Promise<void>;
  logout: () => Promise<void>;
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
      // Beta 模式下，直接尝试获取用户信息，不要先调用 isAuthenticated()
      // 因为在 betaLogin() 刚设置完 cookies 后，可能存在时序问题
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
        return;
      } catch {
        // 如果获取失败，尝试刷新 token
        await refreshToken();
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      }
    } catch (err) {
      // 所有方法都失败，清除状态
      await clearAuth();
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

  const logout = useCallback(async () => {
    // httpOnly cookies 模式：调用后端 logout 清除 cookies
    await clearAuth();
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
