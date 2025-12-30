"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { CheckCircle } from "lucide-react";

import { LearnChatInterface } from "@/components/learn/LearnChatInterface";
import { LearnStepProgress } from "@/components/learn/LearnStepProgress";
import { EmptyState } from "@/components/shared/EmptyState";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { LearnSession, LearnStep } from "@/lib/types";
import { createLearnSession, getLearnSession, updateLearnStep } from "@/lib/learn-api";

export default function LearnPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get("session");
  const [session, setSession] = useState<LearnSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);

  const currentStep = session?.current_step ?? "start";

  useEffect(() => {
    const loadSession = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = sessionId
          ? await getLearnSession(sessionId)
          : await createLearnSession();
        setSession(data);
        if (data.status === "completed") {
          setCompleted(true);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "无法创建学习会话");
      } finally {
        setLoading(false);
      }
    };

    void loadSession();
  }, [sessionId]);

  const refreshSession = async () => {
    if (!session?.id) {
      return;
    }

    try {
      const data = await getLearnSession(session.id);
      setSession(data);
    } catch {
      // keep silent for background refresh
    }
  };

  const handleStepComplete = async (nextStep: LearnStep | null) => {
    if (!session?.id || !nextStep) {
      return;
    }

    try {
      const updated = await updateLearnStep(session.id, nextStep);
      setSession(updated);
    } catch {
      // 静默处理步骤更新失败
    }
  };

  const handleSessionComplete = () => {
    setCompleted(true);
    void refreshSession();
  };

  const handleStartNew = () => {
    router.push("/learn");
    // 强制刷新以创建新会话
    window.location.reload();
  };

  if (loading) {
    return (
      <div className="flex h-[70vh] items-center justify-center">
        <LoadingSpinner label="正在准备学习空间" />
      </div>
    );
  }

  if (error || !session) {
    return (
      <EmptyState
        title="无法进入学习"
        description={error || "学习会话加载失败，请刷新重试。"}
        action={<Button onClick={() => window.location.reload()}>重试</Button>}
      />
    );
  }

  if (completed) {
    return (
      <div className="flex flex-col items-center gap-6 py-12">
        <div className="flex size-20 items-center justify-center rounded-full bg-green-100">
          <CheckCircle className="size-10 text-green-600" />
        </div>
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-foreground">
            学习完成！
          </h2>
          <p className="mt-2 text-muted-foreground">
            太棒了，你已经完成了这次学习
          </p>
        </div>

        {session.review_schedule && (
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-lg">艾宾浩斯复习计划</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm text-muted-foreground">
                根据遗忘曲线，建议在以下时间复习：
              </p>
              <ul className="space-y-1 text-sm">
                <li>📅 1天后：{new Date(session.review_schedule.day_1).toLocaleDateString("zh-CN")}</li>
                <li>📅 3天后：{new Date(session.review_schedule.day_3).toLocaleDateString("zh-CN")}</li>
                <li>📅 7天后：{new Date(session.review_schedule.day_7).toLocaleDateString("zh-CN")}</li>
                <li>📅 15天后：{new Date(session.review_schedule.day_15).toLocaleDateString("zh-CN")}</li>
                <li>📅 30天后：{new Date(session.review_schedule.day_30).toLocaleDateString("zh-CN")}</li>
              </ul>
            </CardContent>
          </Card>
        )}

        <div className="flex gap-4">
          <Button variant="outline" onClick={() => router.push("/dashboard")}>
            返回首页
          </Button>
          <Button onClick={handleStartNew}>
            开始新的学习
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <LearnStepProgress currentStep={currentStep} />

      <LearnChatInterface
        sessionId={session.id}
        initialMessages={session.messages}
        currentStep={currentStep}
        onStreamComplete={refreshSession}
        onStepComplete={handleStepComplete}
        onSessionComplete={handleSessionComplete}
        className="min-h-[520px]"
      />
    </div>
  );
}
