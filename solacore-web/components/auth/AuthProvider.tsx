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
      // 1. 尝试直接获取当前用户
      let currentUser = await getCurrentUser();

      // 2. 如果获取失败（返回 null），尝试刷新 token 再重试
      // 这是为了处理 access token 过期或首次设置 cookie 的情况
      if (!currentUser) {
        try {
          await refreshToken();
          currentUser = await getCurrentUser();
        } catch {
          // 刷新 token 失败，忽略错误，让后续检查处理
        }
      }

      // 3. 最终检查：如果还是没有用户，视为失败
      if (currentUser) {
        setUser(currentUser);
      } else {
        // 明确抛出错误，触发 catch 块的清理逻辑
        throw new Error("无法获取用户信息");
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
