"use client";

import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { login } from "@/lib/auth";
import { useAuth } from "@/components/auth/AuthProvider";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const hasRun = useRef(false);

  const code = useMemo(() => searchParams.get("code"), [searchParams]);
  const redirectTarget = useMemo(() => {
    const state = searchParams.get("state");
    if (!state) {
      return "/dashboard";
    }

    try {
      const parsed = JSON.parse(state) as { redirect?: string };
      return parsed.redirect || "/dashboard";
    } catch {
      return "/dashboard";
    }
  }, [searchParams]);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    if (!code) {
      router.replace("/login?error=missing_code");
      return;
    }

    const verify = async () => {
      try {
        await login(code);
        await refreshUser();
        router.replace(redirectTarget);
      } catch (err) {
        setError(err instanceof Error ? err.message : "登录失败，请重试。");
      }
    };

    void verify();
  }, [code, redirectTarget, refreshUser, router]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background px-6">
        <div className="space-y-4 text-center">
          <p className="text-sm text-destructive">{error}</p>
          <Button onClick={() => router.replace("/login")}>返回登录</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-6">
      <LoadingSpinner label="正在完成验证" />
    </div>
  );
}

export default function CallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-background px-6">
          <LoadingSpinner label="加载中..." />
        </div>
      }
    >
      <CallbackContent />
    </Suspense>
  );
}
