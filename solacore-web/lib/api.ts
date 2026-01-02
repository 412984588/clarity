import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const isBrowser = typeof window !== "undefined";

interface RetryRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // 自动发送 cookies
  xsrfCookieName: "csrf_token", // 后端设置的 CSRF cookie 名称
  xsrfHeaderName: "X-CSRF-Token", // 后端期望的 CSRF header 名称
});

// 设备指纹生成和存储
const getDeviceFingerprint = (): string => {
  if (!isBrowser) {
    return "server-side-render";
  }

  const storageKey = "solacore_device_fingerprint";
  let fingerprint = localStorage.getItem(storageKey);

  if (!fingerprint) {
    // 生成简单的设备指纹：UUID
    fingerprint = crypto.randomUUID();
    localStorage.setItem(storageKey, fingerprint);
  }

  return fingerprint;
};

// 请求拦截器：自动添加设备指纹
api.interceptors.request.use((config) => {
  const fingerprint = getDeviceFingerprint();
  config.headers["X-Device-Fingerprint"] = fingerprint;

  if (process.env.NODE_ENV === "development") {
    console.log("📤 [Request]", {
      url: config.url,
      method: config.method,
      fingerprint,
    });
  }

  return config;
});

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
  const fingerprint = getDeviceFingerprint();

  if (process.env.NODE_ENV === "development") {
    console.log("🔐 [Beta Login] 开始登录", {
      fingerprint,
      device_name: "Web Browser",
      timestamp: new Date().toISOString(),
    });
  }

  // httpOnly cookies 模式：后端会自动设置 cookies，前端无需处理
  // 传递设备指纹，确保后续 API 调用可以识别该设备
  await api.post("/auth/beta-login", {
    device_fingerprint: fingerprint,
    device_name: "Web Browser",
  });

  if (process.env.NODE_ENV === "development") {
    console.log("✅ [Beta Login] 登录成功", { fingerprint });
  }
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

export { api, refreshTokens, betaLogin, getDeviceFingerprint };
