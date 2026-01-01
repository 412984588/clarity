import type { User } from "@/lib/types";
import { api, refreshTokens, getDeviceFingerprint } from "@/lib/api";

interface UserResponse {
  id: string;
  email: string;
  auth_provider: string;
  locale: string;
}

export const login = async (googleCode: string): Promise<void> => {
  // httpOnly cookies 模式：后端会自动设置 cookies，前端无需处理
  // 使用 authorization code flow（更安全）
  const params = new URLSearchParams({
    code: googleCode,
    device_fingerprint: getDeviceFingerprint(), // 使用持久化的设备指纹，与后续 API 请求保持一致
    device_name: navigator.userAgent.substring(0, 50),
  });

  await api.post(`/auth/oauth/google/code?${params.toString()}`);
};

export const logout = async (): Promise<void> => {
  // httpOnly cookies 模式：调用后端 logout 清除 cookies
  await api.post("/auth/logout");
};

export const getCurrentUser = async (): Promise<User | null> => {
  try {
    // httpOnly cookies 模式：调用 /auth/me API 获取当前用户
    const response = await api.get<UserResponse>("/auth/me");
    const data = response.data;

    // 获取订阅信息
    let subscriptionTier: "free" | "standard" | "pro" = "free";
    try {
      const subResponse = await api.get<{ tier: string }>(
        "/subscriptions/current",
      );
      const tier = subResponse.data.tier;
      // 验证 tier 是否为有效值
      if (tier === "free" || tier === "standard" || tier === "pro") {
        subscriptionTier = tier;
      }
    } catch {
      // 订阅信息获取失败，默认 free
    }

    return {
      id: data.id,
      email: data.email,
      name: data.email.split("@")[0], // 临时从 email 生成 name
      picture: undefined,
      subscription_tier: subscriptionTier,
      created_at: new Date().toISOString(),
    };
  } catch {
    return null;
  }
};

export const isAuthenticated = async (): Promise<boolean> => {
  try {
    // httpOnly cookies 模式：调用 /auth/me API 验证登录状态
    await api.get("/auth/me");
    return true;
  } catch {
    return false;
  }
};

export const refreshToken = async (): Promise<void> => {
  // httpOnly cookies 模式：调用 refresh API，cookies 会自动更新
  await refreshTokens();
};
