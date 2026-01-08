"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import { Download } from "lucide-react";

import { ChatInterface } from "@/components/solve/ChatInterface";
import { StepProgress } from "@/components/solve/StepProgress";
import { EmptyState } from "@/components/shared/EmptyState";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import { ReminderPicker } from "@/components/session/ReminderPicker";
import { ActionPlanCard } from "@/components/session/ActionPlanCard";
import { TagInput } from "@/components/session/TagInput";
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

  const handleTagsChange = async (tags: string[]) => {
    if (!sessionId) return;

    try {
      await updateSession(sessionId, { tags });
      setSession((prev) => (prev ? { ...prev, tags } : null));
      toast.success("标签已更新");
    } catch (err) {
      toast.error("更新标签失败");
      console.error(err);
    }
  };

  const handleExport = async (format: "markdown" | "json") => {
    if (!sessionId) return;

    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${API_URL}/sessions/${sessionId}/export?format=${format}`,
        { credentials: "include" },
      );

      if (!response.ok) {
        throw new Error("导出失败");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      const contentDisposition = response.headers.get("Content-Disposition");
      const filename =
        contentDisposition?.split("filename=")[1]?.replace(/"/g, "") ||
        `session_${sessionId}.${format === "markdown" ? "md" : "json"}`;

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast.success(`导出成功：${filename}`);
    } catch (err) {
      toast.error("导出失败");
      console.error(err);
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
        <div className="flex items-center gap-2">
          <ReminderPicker
            value={reminderTime}
            onChange={handleReminderChange}
          />
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport("markdown")}
          >
            <Download className="w-4 h-4 mr-2" />
            导出
          </Button>
        </div>
      </div>
      {session.first_step_action && (
        <ActionPlanCard
          sessionId={session.id}
          action={session.first_step_action}
          completed={session.action_completed || false}
          onToggle={handleActionToggle}
        />
      )}
      <div className="border rounded-lg p-4 bg-white">
        <h3 className="text-sm font-medium text-gray-700 mb-2">标签</h3>
        <TagInput
          value={session.tags || []}
          onChange={handleTagsChange}
          placeholder="添加标签以便分类..."
        />
      </div>
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
