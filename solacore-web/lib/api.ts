import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const isBrowser = typeof window !== "undefined";

interface RetryRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // 自动发送 cookies
});

// httpOnly cookies 模式：浏览器会自动发送 cookies，无需手动添加 Authorization 头
// 移除了原有的请求拦截器

let refreshPromise: Promise<void> | null = null;

const refreshTokens = async (): Promise<void> => {
  if (refreshPromise) {
    return refreshPromise;
  }

  // httpOnly cookies 模式：后端从 cookie 读取 refresh_token，前端不需要传递
  refreshPromise = api
    .post("/auth/refresh")
    .then(() => {
      // httpOnly cookies 模式：token 存储在 cookie 中，前端无需处理
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
};

const betaLogin = async (): Promise<void> => {
  // httpOnly cookies 模式：后端会自动设置 cookies，前端无需处理
  await api.post("/auth/beta-login");
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const status = error.response?.status;
    const originalRequest = error.config as RetryRequestConfig | undefined;

    const isAuthRefresh = originalRequest?.url?.includes("/auth/refresh");
    const isAuthLogin = originalRequest?.url?.includes("/auth/login");

    // 401 错误：尝试刷新 token
    if (
      status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isAuthRefresh &&
      !isAuthLogin
    ) {
      originalRequest._retry = true;

      try {
        await refreshTokens();
        // httpOnly cookies 模式：token 已自动更新在 cookie 中
        return api.request(originalRequest);
      } catch (refreshError) {
        // refresh 失败，清除 cookies 并跳转登录页
        if (isBrowser) {
          // 🚨 Gemini 修复：如果已经在登录页，不要再重定向，避免无限循环
          if (!window.location.pathname.startsWith("/login")) {
            // httpOnly cookies 由后端管理，前端调用 /auth/logout 清除
            await api.post("/auth/logout").catch(() => {
              // 忽略 logout 错误
            });
            window.location.href = "/login?cause=auth_error";
          }
        }
        return Promise.reject(refreshError);
      }
    }

    // 其他 401 错误：清除 cookies 并跳转登录页
    if (status === 401) {
      if (isBrowser) {
        // 🚨 Gemini 修复：如果已经在登录页，不要再重定向，避免无限循环
        if (!window.location.pathname.startsWith("/login")) {
          // httpOnly cookies 由后端管理，前端调用 /auth/logout 清除
          await api.post("/auth/logout").catch(() => {
            // 忽略 logout 错误
          });
          window.location.href = "/login?cause=auth_error";
        }
      }
    }

    return Promise.reject(error);
  },
);

export { api, refreshTokens, betaLogin };
