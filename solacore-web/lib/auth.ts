import { jwtDecode } from "jwt-decode";

import type { AuthTokens, User } from "@/lib/types";
import {
  api,
  clearStoredTokens,
  getStoredTokens,
  refreshTokens,
  setStoredTokens,
} from "@/lib/api";

interface TokenPayload {
  sub?: string;
  user_id?: string;
  email?: string;
  name?: string;
  picture?: string;
  subscription_tier?: "free" | "standard" | "pro";
  created_at?: string;
  exp?: number;
}

export const login = async (googleToken: string): Promise<AuthTokens> => {
  const response = await api.post<AuthTokens>("/auth/login/google", {
    token: googleToken,
    code: googleToken,
  });
  setStoredTokens(response.data);
  return response.data;
};

export const logout = (): void => {
  clearStoredTokens();
};

export const getCurrentUser = (): User | null => {
  const token = getStoredTokens()?.access_token;
  if (!token) {
    return null;
  }

  try {
    const payload = jwtDecode<TokenPayload>(token);
    const id = payload.sub ?? payload.user_id ?? "";

    return {
      id,
      email: payload.email ?? "",
      name: payload.name ?? "",
      picture: payload.picture,
      subscription_tier: payload.subscription_tier ?? "free",
      created_at: payload.created_at ?? new Date().toISOString(),
    };
  } catch {
    return null;
  }
};

export const isAuthenticated = (): boolean => {
  const token = getStoredTokens()?.access_token;
  if (!token) {
    return false;
  }

  try {
    const payload = jwtDecode<TokenPayload>(token);
    if (!payload.exp) {
      return true;
    }
    return payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
};

export const refreshToken = async (): Promise<AuthTokens> => {
  const tokens = await refreshTokens();
  return tokens;
};
