"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Trash2 } from "lucide-react";

import { ChatInterface } from "@/components/solve/ChatInterface";
import { OptionCard } from "@/components/solve/OptionCard";
import { StepProgress } from "@/components/solve/StepProgress";
import { EmptyState } from "@/components/shared/EmptyState";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Session } from "@/lib/types";
import { createSession, getSession, deleteSession } from "@/lib/session-api";

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
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOptions, setSelectedOptions] = useState<Set<string>>(
    () => new Set(),
  );
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

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

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!session?.id) return;

    setDeleting(true);
    try {
      await deleteSession(session.id);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "删除会话失败");
      setDeleteDialogOpen(false);
    } finally {
      setDeleting(false);
    }
  };

  const handleCancelDelete = () => {
    setDeleteDialogOpen(false);
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
      <div className="flex items-center justify-between">
        <StepProgress currentStep={currentStep} />
        <Button
          variant="ghost"
          size="icon"
          onClick={handleDeleteClick}
          aria-label="删除会话"
          title="删除当前会话"
        >
          <Trash2 className="size-5 text-muted-foreground hover:text-destructive" />
        </Button>
      </div>

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

      {/* 删除确认对话框 */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除会话</DialogTitle>
            <DialogDescription>
              您确定要删除当前会话吗？此操作无法撤销，会话的所有消息和历史记录都将被永久删除。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={handleCancelDelete}
              disabled={deleting}
            >
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={deleting}
            >
              {deleting ? "删除中..." : "确认删除"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
