"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Mail } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { api } from "@/lib/api";

const SUCCESS_MESSAGE = "如果该邮箱存在，将收到重置链接";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const redirectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("请输入有效的邮箱地址");
      return;
    }

    setIsLoading(true);

    try {
      await api.post("/auth/forgot-password", {
        email,
      });

      setMessage(SUCCESS_MESSAGE);

      if (redirectTimerRef.current) {
        clearTimeout(redirectTimerRef.current);
      }
      redirectTimerRef.current = setTimeout(() => {
        router.push("/login");
      }, 3000);
    } catch {
      setError("发送失败，请稍后重试");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (redirectTimerRef.current) {
        clearTimeout(redirectTimerRef.current);
      }
    };
  }, []);

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
              重置你的密码
              <span className="block text-foreground">重新开始对话</span>
            </h1>
            <p className="max-w-md text-base leading-relaxed text-muted-foreground">
              输入你的邮箱地址，我们会发送一封重置密码的邮件。
            </p>
            <div className="grid gap-4 pt-2">
              <div className="flex items-start gap-3">
                <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-amber-100 text-sm font-medium text-amber-700">
                  1
                </div>
                <div>
                  <p className="font-medium text-foreground">安全验证</p>
                  <p className="text-sm text-muted-foreground">
                    系统会验证邮箱与账户状态
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-sm font-medium text-emerald-700">
                  2
                </div>
                <div>
                  <p className="font-medium text-foreground">邮件重置</p>
                  <p className="text-sm text-muted-foreground">
                    点击邮件中的链接设置新密码
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
                  <CardTitle className="text-2xl">找回密码</CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
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
                    disabled={isLoading}
                  />
                </div>

                {message ? (
                  <p className="text-sm text-emerald-600">{message}</p>
                ) : null}
                {error ? (
                  <p className="text-sm text-destructive">{error}</p>
                ) : null}

                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? (
                    <LoadingSpinner label="" />
                  ) : (
                    <>
                      <Mail className="size-4" />
                      发送重置链接
                    </>
                  )}
                </Button>

                <p className="text-center text-sm text-muted-foreground">
                  已经想起密码？{" "}
                  <Link
                    href="/login"
                    className="font-medium text-foreground hover:underline"
                  >
                    返回登录
                  </Link>
                </p>

                <p className="text-xs text-muted-foreground">
                  我们将发送一封包含重置链接的邮件。
                </p>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
