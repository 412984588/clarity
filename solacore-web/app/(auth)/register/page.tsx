"use client";

import { Suspense, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Eye, EyeOff, UserPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { api, getDeviceFingerprint } from "@/lib/api";
import { useAuth } from "@/components/auth/AuthProvider";

interface RegisterError {
  response?: {
    data?: {
      detail?: string;
    };
  };
}

function RegisterContent() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 密码验证：8+ 字符，1 个大写字母，1 个数字
  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) {
      return "密码至少需要 8 个字符";
    }
    if (!/[A-Z]/.test(pwd)) {
      return "密码需要包含至少 1 个大写字母";
    }
    if (!/\d/.test(pwd)) {
      return "密码需要包含至少 1 个数字";
    }
    return null;
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("请输入有效的邮箱地址");
      return;
    }

    // 验证密码强度
    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    // 验证密码一致
    if (password !== confirmPassword) {
      setError("两次输入的密码不一致");
      return;
    }

    setLoading(true);

    try {
      const fingerprint = getDeviceFingerprint();

      await api.post("/auth/register", {
        email,
        password,
        device_fingerprint: fingerprint,
        device_name: "Web Browser",
      });

      // 注册成功后刷新用户状态并跳转
      await refreshUser();
      router.replace("/dashboard");
    } catch (err) {
      const registerError = err as RegisterError;
      const detail = registerError.response?.data?.detail;

      if (
        detail?.includes("already registered") ||
        detail?.includes("已存在")
      ) {
        setError("该邮箱已被注册，请直接登录或使用其他邮箱");
      } else if (detail) {
        setError(detail);
      } else {
        setError("注册失败，请稍后重试");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,#fef3c7,transparent_45%),radial-gradient(circle_at_bottom,#c7f9e8,transparent_45%)]">
      <div className="absolute -left-24 -top-24 size-72 rounded-full bg-amber-200/50 blur-3xl" />
      <div className="absolute -bottom-32 right-0 size-96 rounded-full bg-emerald-200/60 blur-3xl" />

      <div className="relative mx-auto flex min-h-screen max-w-5xl items-center justify-center px-6 py-16">
        <div className="grid w-full gap-10 md:grid-cols-[1.1fr_0.9fr]">
          <div className="flex flex-col justify-center gap-6 text-left">
            <div className="inline-flex items-center gap-3 text-sm font-semibold uppercase tracking-[0.3em] text-foreground/70">
              <span className="h-px w-12 bg-foreground/40" />
              Solacore Web
            </div>
            <h1 className="text-4xl font-semibold leading-tight text-foreground md:text-5xl">
              开始你的
              <span className="block text-foreground">清晰之旅</span>
            </h1>
            <p className="max-w-md text-base leading-relaxed text-muted-foreground">
              注册 Solacore，开启五步思考流程，将复杂情绪转化为清晰行动
            </p>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <div className="rounded-full border px-3 py-1">免费使用</div>
              <div className="rounded-full border px-3 py-1">安全加密</div>
              <div className="rounded-full border px-3 py-1">隐私保护</div>
            </div>
          </div>

          <Card className="border-foreground/10 bg-background/80 shadow-xl backdrop-blur">
            <CardHeader className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex size-10 items-center justify-center rounded-2xl bg-foreground text-base font-semibold text-background">
                  C
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">
                    Solacore
                  </p>
                  <CardTitle className="text-2xl">创建账号</CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleRegister} className="space-y-4">
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
                      placeholder="至少 8 位，含大写字母和数字"
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

                <div className="space-y-2">
                  <label
                    htmlFor="confirmPassword"
                    className="text-sm font-medium"
                  >
                    确认密码
                  </label>
                  <div className="relative">
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      placeholder="再次输入密码"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                      disabled={loading}
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() =>
                        setShowConfirmPassword(!showConfirmPassword)
                      }
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showConfirmPassword ? (
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
                      <UserPlus className="size-4" />
                      注册
                    </>
                  )}
                </Button>

                <p className="text-center text-sm text-muted-foreground">
                  已有账号？{" "}
                  <Link
                    href="/login"
                    className="font-medium text-foreground hover:underline"
                  >
                    立即登录
                  </Link>
                </p>

                <p className="text-xs text-muted-foreground">
                  注册即表示你同意 Solacore 的服务条款与隐私政策
                </p>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-background">
          <LoadingSpinner label="加载中..." />
        </div>
      }
    >
      <RegisterContent />
    </Suspense>
  );
}
