"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

import { ChatInterface } from "@/components/solve/ChatInterface";
import { OptionCard } from "@/components/solve/OptionCard";
import { StepProgress } from "@/components/solve/StepProgress";
import { EmptyState } from "@/components/shared/EmptyState";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import type { Session } from "@/lib/types";
import { createSession, getSession } from "@/lib/session-api";

const optionDeck = [
  {
    id: "solacore-map",
    title: "情绪地图",
    description: "梳理核心情绪与触发点，确认真实需求。",
  },
  {
    id: "micro-steps",
    title: "微行动计划",
    description: "把目标拆成 3 步以内的可执行动作。",
  },
  {
    id: "support-circle",
    title: "支持系统",
    description: "识别可以帮助你的人与资源，设置请求方式。",
  },
];

export default function SolvePage() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOptions, setSelectedOptions] = useState<Set<string>>(
    () => new Set(),
  );

  const currentStep = session?.current_step ?? "receive";

  const optionsVisible = useMemo(
    () => currentStep === "options",
    [currentStep],
  );

  useEffect(() => {
    const loadSession = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = sessionId
          ? await getSession(sessionId)
          : await createSession();
        setSession(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "无法创建会话");
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
      const data = await getSession(session.id);
      setSession(data);
    } catch {
      // keep silent for background refresh
    }
  };

  const toggleOption = (id: string) => {
    setSelectedOptions((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  if (loading) {
    return (
      <div className="flex h-[70vh] items-center justify-center">
        <LoadingSpinner label="正在准备会话" />
      </div>
    );
  }

  if (error || !session) {
    return (
      <EmptyState
        title="无法进入对话"
        description={error || "会话加载失败，请刷新重试。"}
        action={<Button onClick={() => window.location.reload()}>重试</Button>}
      />
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <StepProgress currentStep={currentStep} />

      <ChatInterface
        sessionId={session.id}
        initialMessages={session.messages}
        currentStep={currentStep}
        onStreamComplete={refreshSession}
        className="min-h-[520px]"
      />

      {optionsVisible ? (
        <div className="grid gap-4 md:grid-cols-3">
          {optionDeck.map((option) => (
            <OptionCard
              key={option.id}
              title={option.title}
              description={option.description}
              selected={selectedOptions.has(option.id)}
              onToggle={() => toggleOption(option.id)}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}
