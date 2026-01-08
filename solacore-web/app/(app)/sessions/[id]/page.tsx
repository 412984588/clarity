"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";

import { ChatInterface } from "@/components/solve/ChatInterface";
import { StepProgress } from "@/components/solve/StepProgress";
import { EmptyState } from "@/components/shared/EmptyState";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import { ReminderPicker } from "@/components/session/ReminderPicker";
import { ActionPlanCard } from "@/components/session/ActionPlanCard";
import type { Session } from "@/lib/types";
import { getSession, updateSession } from "@/lib/session-api";
import { completeAction, uncompleteAction } from "@/lib/action-api";

export default function SessionDetailPage() {
  const params = useParams<{ id: string }>();
  const sessionId = Array.isArray(params?.id) ? params?.id[0] : params?.id;
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reminderTime, setReminderTime] = useState<Date | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setError("缺少会话 ID");
      setLoading(false);
      return;
    }

    const load = async () => {
      try {
        const data = await getSession(sessionId);
        setSession(data);
        setReminderTime(
          data.reminder_time ? new Date(data.reminder_time) : null,
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "加载会话失败");
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [sessionId]);

  const handleReminderChange = async (date: Date | null) => {
    if (!sessionId) return;

    try {
      await updateSession(sessionId, {
        reminder_time: date?.toISOString() ?? null,
      });
      setReminderTime(date);
      toast.success(date ? "提醒已设置" : "提醒已取消");
    } catch (err) {
      toast.error("更新提醒失败");
      console.error(err);
    }
  };

  const handleActionToggle = async (completed: boolean) => {
    if (!sessionId) return;

    if (completed) {
      await completeAction(sessionId);
    } else {
      await uncompleteAction(sessionId);
    }
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <LoadingSpinner label="加载会话" />
      </div>
    );
  }

  if (error || !session) {
    return (
      <EmptyState
        title="无法打开会话"
        description={error || "请返回会话列表重试。"}
        action={
          <Button asChild>
            <Link href="/sessions">返回列表</Link>
          </Button>
        }
      />
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <StepProgress currentStep={session.current_step} />
        <ReminderPicker value={reminderTime} onChange={handleReminderChange} />
      </div>
      {session.first_step_action && (
        <ActionPlanCard
          sessionId={session.id}
          action={session.first_step_action}
          completed={session.action_completed || false}
          onToggle={handleActionToggle}
        />
      )}
      <ChatInterface
        sessionId={session.id}
        initialMessages={session.messages}
        readonly
      />
      {session.status !== "completed" ? (
        <Button asChild>
          <Link href={`/solve?session=${session.id}`}>继续</Link>
        </Button>
      ) : null}
    </div>
  );
}
