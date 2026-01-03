"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { KeyRound, Lock, ShieldCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { api } from "@/lib/api";

interface ResetError {
  response?: {
    data?: {
      error?: string;
      detail?: string;
    };
  };
}

const passwordRules = [
  { key: "length", label: "至少 8 位字符" },
  { key: "upper", label: "包含大写字母" },
  { key: "lower", label: "包含小写字母" },
  { key: "digit", label: "包含数字" },
] as const;

type RuleKey = (typeof passwordRules)[number]["key"];

type RuleState = Record<RuleKey, boolean>;

const evaluatePassword = (value: string): RuleState => ({
  length: value.length >= 8,
  upper: /[A-Z]/.test(value),
  lower: /[a-z]/.test(value),
  digit: /\d/.test(value),
});

function ResetPasswordContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = useMemo(() => searchParams.get("token"), [searchParams]);

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const ruleState = useMemo(() => evaluatePassword(password), [password]);
  const isPasswordValid = Object.values(ruleState).every(Boolean);
  const isMatch = password.length > 0 && password === confirmPassword;

  useEffect(() => {
    if (!token) {
      setError("无效的重置链接");
    }
  }, [token]);

  useEffect(() => {
    if (!success) {
      return;
    }

    const timer = window.setTimeout(() => {
      router.push("/login");
    }, 3000);

    return () => window.clearTimeout(timer);
  }, [router, success]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    if (!token) {
      setError("无效的重置链接");
      return;
    }

    if (!isPasswordValid) {
      setError("请设置更强的密码");
      return;
    }

    if (!isMatch) {
      setError("两次密码输入不一致");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post<{ message: string }>(
        "/auth/reset-password",
        {
          token,
          new_password: password,
        },
      );

      setSuccess(response.data.message || "密码重置成功，正在跳转...");
    } catch (err) {
      const resetError = err as ResetError;
      const code = resetError.response?.data?.error;
      const detail = resetError.response?.data?.detail;

      if (code === "INVALID_OR_EXPIRED_TOKEN") {
        setError("链接已过期，请重新申请");
      } else if (typeof detail === "string" && detail.length > 0) {
        setError(detail);
      } else {
        setError("重置失败，请重试");
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
          <div className="order-2 flex flex-col justify-center gap-6 text-left md:order-1">
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
              重新设定你的
              <span className="block text-foreground">安全密码</span>
            </h1>
            <p className="max-w-md text-base leading-relaxed text-muted-foreground">
              设定更安全的登录方式，继续使用 Solacore 的清晰思考流程。
            </p>
            <div className="grid gap-4 pt-2">
              <div className="flex items-start gap-3">
                <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-amber-100 text-sm font-medium text-amber-700">
                  <ShieldCheck className="size-4" />
                </div>
                <div>
                  <p className="font-medium text-foreground">强化安全</p>
                  <p className="text-sm text-muted-foreground">
                    建议定期更新密码并避免重复使用
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-sm font-medium text-emerald-700">
                  <KeyRound className="size-4" />
                </div>
                <div>
                  <p className="font-medium text-foreground">快速恢复</p>
                  <p className="text-sm text-muted-foreground">
                    完成重置后 3 秒自动跳转登录
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-medium text-blue-700">
                  <Lock className="size-4" />
                </div>
                <div>
                  <p className="font-medium text-foreground">私密保障</p>
                  <p className="text-sm text-muted-foreground">
                    使用专属链接安全重置密码
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
                  <CardTitle className="text-2xl">重置密码</CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="password" className="text-sm font-medium">
                    新密码
                  </label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="至少 8 位字符"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                    disabled={loading}
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="confirmPassword"
                    className="text-sm font-medium"
                  >
                    确认密码
                  </label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="再次输入新密码"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    required
                    disabled={loading}
                  />
                </div>

                <div className="rounded-lg border border-foreground/10 bg-background/70 p-3">
                  <p className="text-xs font-medium text-muted-foreground">
                    密码强度要求
                  </p>
                  <ul className="mt-2 space-y-1 text-xs">
                    {passwordRules.map((rule) => {
                      const ok = ruleState[rule.key];
                      return (
                        <li
                          key={rule.key}
                          className={
                            ok ? "text-emerald-600" : "text-muted-foreground"
                          }
                        >
                          {ok ? "✓" : "•"} {rule.label}
                        </li>
                      );
                    })}
                  </ul>
                </div>

                {!isMatch && confirmPassword.length > 0 ? (
                  <p className="text-sm text-destructive">两次密码输入不一致</p>
                ) : null}

                {error ? (
                  <p className="text-sm text-destructive">{error}</p>
                ) : null}

                {success ? (
                  <p className="text-sm text-emerald-600">{success}</p>
                ) : null}

                <Button
                  type="submit"
                  className="w-full"
                  disabled={loading || !token}
                >
                  {loading ? <LoadingSpinner label="" /> : "重置密码"}
                </Button>

                <p className="text-center text-sm text-muted-foreground">
                  记得密码了？{" "}
                  <Link
                    href="/login"
                    className="font-medium text-foreground hover:underline"
                  >
                    返回登录
                  </Link>
                </p>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-background">
          <LoadingSpinner label="加载中..." />
        </div>
      }
    >
      <ResetPasswordContent />
    </Suspense>
  );
}
