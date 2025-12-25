"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/auth/AuthProvider";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { api, betaLogin } from "@/lib/api";

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) {
      return;
    }

    if (user) {
      router.replace("/dashboard");
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
            await betaLogin();
            if (isActive) {
              router.replace("/dashboard");
            }
            return;
          } catch (loginError) {
            console.error("Failed to beta login:", loginError);
          }
        }
      } catch (checkError) {
        console.error("Failed to check beta mode:", checkError);
      }

      if (isActive) {
        router.replace("/login");
      }
    };

    void checkBetaMode();

    return () => {
      isActive = false;
    };
  }, [loading, user, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <LoadingSpinner label="跳转中..." />
    </div>
  );
}
