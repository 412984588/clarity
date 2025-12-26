import type { User } from "@/lib/types";
import { api, refreshTokens } from "@/lib/api";

interface UserResponse {
  id: string;
  email: string;
  auth_provider: string;
  locale: string;
}

export const login = async (googleToken: string): Promise<void> => {
  // httpOnly cookies 模式：后端会自动设置 cookies，前端无需处理
  await api.post("/auth/login/google", {
    token: googleToken,
    code: googleToken,
  });
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

    return {
      id: data.id,
      email: data.email,
      name: data.email.split("@")[0], // 临时从 email 生成 name
      picture: undefined,
      subscription_tier: "free", // 后续从后端获取
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
