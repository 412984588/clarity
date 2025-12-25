import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

import type { AuthTokens } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const STORAGE_KEY = "solacore_auth_tokens";

const isBrowser = typeof window !== "undefined";

interface RetryRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

const readTokens = (): AuthTokens | null => {
  if (!isBrowser) {
    return null;
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as AuthTokens;
  } catch {
    return null;
  }
};

const writeTokens = (tokens: AuthTokens): void => {
  if (!isBrowser) {
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens));
};

const clearTokens = (): void => {
  if (!isBrowser) {
    return;
  }

  window.localStorage.removeItem(STORAGE_KEY);
};

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const stored = readTokens();
  const token = stored?.access_token;
  if (token) {
    const tokenType = stored?.token_type ?? "Bearer";
    config.headers = config.headers ?? {};
    config.headers.Authorization = `${tokenType} ${token}`;
  }
  return config;
});

let refreshPromise: Promise<AuthTokens> | null = null;

const refreshTokens = async (): Promise<AuthTokens> => {
  if (refreshPromise) {
    return refreshPromise;
  }

  const stored = readTokens();
  if (!stored?.refresh_token) {
    throw new Error("Missing refresh token");
  }

  refreshPromise = axios
    .post<AuthTokens>(`${API_BASE_URL}/auth/refresh`, {
      refresh_token: stored.refresh_token,
    })
    .then((response) => {
      writeTokens(response.data);
      return response.data;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
};

const betaLogin = async (): Promise<void> => {
  const response = await api.post<{
    access_token: string;
    refresh_token: string;
    token_type?: string;
  }>("/auth/beta-login");

  writeTokens({
    access_token: response.data.access_token,
    refresh_token: response.data.refresh_token,
    token_type: response.data.token_type ?? "Bearer",
  });
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const status = error.response?.status;
    const originalRequest = error.config as RetryRequestConfig | undefined;

    const isAuthRefresh = originalRequest?.url?.includes("/auth/refresh");
    const isAuthLogin = originalRequest?.url?.includes("/auth/login");

    if (
      status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isAuthRefresh &&
      !isAuthLogin
    ) {
      originalRequest._retry = true;

      try {
        const tokens = await refreshTokens();
        const tokenType = tokens.token_type ?? "Bearer";
        originalRequest.headers = originalRequest.headers ?? {};
        originalRequest.headers.Authorization = `${tokenType} ${tokens.access_token}`;
        return api.request(originalRequest);
      } catch (refreshError) {
        clearTokens();
        if (isBrowser) {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      }
    }

    if (status === 401) {
      clearTokens();
      if (isBrowser) {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  },
);

export {
  api,
  readTokens as getStoredTokens,
  writeTokens as setStoredTokens,
  clearTokens as clearStoredTokens,
  refreshTokens,
  betaLogin,
};
