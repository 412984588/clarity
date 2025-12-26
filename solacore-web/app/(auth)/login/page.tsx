"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Eye, EyeOff, LogIn } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { useAuth } from "@/components/auth/AuthProvider";
import { api, betaLogin, getDeviceFingerprint } from "@/lib/api";

interface LoginError {
  response?: {
    data?: {
      detail?: string | { error?: string };
    };
  };
}

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, refreshUser } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 检查是否因认证错误重定向过来（防止无限循环）
  const isAuthError = searchParams.get("cause") === "auth_error";
  const [checkingBeta, setCheckingBeta] = useState(!isAuthError);

  const redirectPath = useMemo(() => {
    return searchParams.get("redirect") || "/dashboard";
  }, [searchParams]);

  useEffect(() => {
    // 如果是认证错误，直接跳过自动登录
    if (isAuthError) {
      return;
    }

    let isActive = true;

    const checkBetaMode = async () => {
      try {
        const response = await api.get<{ beta_mode: boolean }>(
          "/auth/config/features",
        );

        if (response.data.beta_mode) {
          try {
            // Beta 模式：自动登录
            await betaLogin();
            await refreshUser();
            router.replace("/dashboard");
            return;
          } catch (loginError) {
            console.error("Failed to beta login:", loginError);
          }
        }
      } catch (checkError) {
        console.error("Failed to check beta mode:", checkError);
      }

      if (isActive) {
        setCheckingBeta(false);
      }
    };

    // 如果 Context 里已经有 user 了，直接跳转
    if (user) {
      router.replace(redirectPath);
      return;
    }

    void checkBetaMode();

    return () => {
      isActive = false;
    };
  }, [router, user, refreshUser, redirectPath, isAuthError]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("请输入有效的邮箱地址");
      return;
    }

    if (!password) {
      setError("请输入密码");
      return;
    }

    setLoading(true);

    try {
      const fingerprint = getDeviceFingerprint();

      await api.post("/auth/login", {
        email,
        password,
        device_fingerprint: fingerprint,
        device_name: "Web Browser",
      });

      // 登录成功后刷新用户状态并跳转
      await refreshUser();
      router.replace(redirectPath);
    } catch (err) {
      const loginError = err as LoginError;
      const detail = loginError.response?.data?.detail;

      if (typeof detail === "object" && detail?.error) {
        if (detail.error === "INVALID_CREDENTIALS") {
          setError("邮箱或密码错误");
        } else if (detail.error === "DEVICE_LIMIT_REACHED") {
          setError("设备数量已达上限，请先退出其他设备");
        } else {
          setError(detail.error);
        }
      } else if (typeof detail === "string") {
        setError(detail);
      } else {
        setError("登录失败，请稍后重试");
      }
    } finally {
      setLoading(false);
    }
  };

  if (checkingBeta) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <LoadingSpinner label="加载中..." />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,#fef3c7,transparent_45%),radial-gradient(circle_at_bottom,#c7f9e8,transparent_45%)]">
      <div className="absolute -left-24 -top-24 size-72 rounded-full bg-amber-200/50 blur-3xl" />
      <div className="absolute -bottom-32 right-0 size-96 rounded-full bg-emerald-200/60 blur-3xl" />

      <div className="relative mx-auto flex min-h-screen max-w-5xl items-center justify-center px-6 py-16">
        <div className="grid w-full gap-10 md:grid-cols-[1.1fr_0.9fr]">
          <div className="order-2 flex flex-col justify-center gap-6 text-left md:order-1">
            {/* Solacore Logo */}
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-full bg-gradient-to-br from-amber-200 to-emerald-200 shadow-sm">
                <span className="text-base font-semibold text-foreground/80">
                  S
                </span>
              </div>
              <div>
                <span className="text-xl font-semibold tracking-tight text-foreground">
                  Solacore
                </span>
                <span className="ml-1.5 text-sm font-normal text-muted-foreground">
                  Web
                </span>
              </div>
            </div>
            <h1 className="text-4xl font-semibold leading-tight text-foreground md:text-5xl">
              帮你把复杂情绪转成
              <span className="block text-foreground">清晰行动</span>
            </h1>
            <p className="max-w-md text-base leading-relaxed text-muted-foreground">
              从澄清到承诺，Solacore 带你完成五步思考流程，留下可执行的下一步。
            </p>
            <div className="grid gap-4 pt-2">
              <div className="flex items-start gap-3">
                <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-amber-100 text-sm font-medium text-amber-700">
                  1
                </div>
                <div>
                  <p className="font-medium text-foreground">私密对话</p>
                  <p className="text-sm text-muted-foreground">
                    说出你的困扰，不用担心条理
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-sm font-medium text-emerald-700">
                  2
                </div>
                <div>
                  <p className="font-medium text-foreground">结构化引导</p>
                  <p className="text-sm text-muted-foreground">
                    Solacore 引导你看清问题本质
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-medium text-blue-700">
                  3
                </div>
                <div>
                  <p className="font-medium text-foreground">立即可用</p>
                  <p className="text-sm text-muted-foreground">
                    得到清晰可执行的下一步
                  </p>
                </div>
              </div>
            </div>
          </div>

          <Card className="order-1 border-foreground/10 bg-background/80 shadow-xl backdrop-blur md:order-2">
            <CardHeader className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex size-10 items-center justify-center rounded-2xl bg-foreground text-base font-semibold text-background">
                  S
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">
                    Solacore
                  </p>
                  <CardTitle className="text-2xl">欢迎回来</CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium">
                    邮箱地址
                  </label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={loading}
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="password" className="text-sm font-medium">
                    密码
                  </label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="输入密码"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      disabled={loading}
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? (
                        <EyeOff className="size-4" />
                      ) : (
                        <Eye className="size-4" />
                      )}
                    </button>
                  </div>
                </div>

                {error ? (
                  <p className="text-sm text-destructive">{error}</p>
                ) : null}

                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? (
                    <LoadingSpinner label="" />
                  ) : (
                    <>
                      <LogIn className="size-4" />
                      登录
                    </>
                  )}
                </Button>

                <p className="text-center text-sm text-muted-foreground">
                  还没有账号？{" "}
                  <Link
                    href="/register"
                    className="font-medium text-foreground hover:underline"
                  >
                    立即注册
                  </Link>
                </p>

                <p className="text-xs text-muted-foreground">
                  登录即表示你同意 Solacore 的
                  <Link href="/terms" className="underline">
                    服务条款
                  </Link>
                  与
                  <Link href="/privacy" className="underline">
                    隐私政策
                  </Link>
                  。
                </p>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-background">
          <LoadingSpinner label="加载中..." />
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}
