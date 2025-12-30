"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { SendHorizontal, BookOpen } from "lucide-react";

import type { LearnMessage, LearnStep } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useLearnChatStream } from "@/hooks/useLearnChatStream";

interface LearnChatInterfaceProps {
  sessionId: string;
  initialMessages?: LearnMessage[];
  currentStep?: LearnStep;
  readonly?: boolean;
  className?: string;
  onStreamComplete?: () => void;
  onStepComplete?: (nextStep: LearnStep | null) => void;
  onSessionComplete?: () => void;
}

// 根据步骤显示不同的提示文字
const STEP_PLACEHOLDERS: Record<LearnStep, string> = {
  start: "告诉我你想学习什么...",
  explore: "分享你的理解，或者问我任何问题...",
  practice: "试着用自己的话解释，或回答练习题...",
  plan: "告诉我你的学习目标和计划...",
};

export function LearnChatInterface({
  sessionId,
  initialMessages = [],
  currentStep = "start",
  readonly = false,
  className,
  onStreamComplete,
  onStepComplete,
  onSessionComplete,
}: LearnChatInterfaceProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const { messages, sending, handleSend, setMessages } = useLearnChatStream({
    sessionId,
    currentStep,
    onStreamComplete,
    onStepComplete,
    onSessionComplete,
  });

  // 只在 sessionId 变化时重置消息
  useEffect(() => {
    if (sessionId) {
      setMessages(initialMessages);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const messageCountLabel = useMemo(() => {
    return `${messages.length} 条消息`;
  }, [messages.length]);

  const onSendClick = async () => {
    if (!input.trim() || sending || readonly) {
      return;
    }

    const trimmed = input.trim();
    setInput("");
    await handleSend(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void onSendClick();
    }
  };

  return (
    <div
      className={cn(
        "flex h-full flex-col rounded-3xl border bg-card/80 shadow-sm",
        className
      )}
    >
      <div className="flex items-center justify-between border-b px-6 py-4">
        <div className="flex items-center gap-2">
          <BookOpen className="size-5 text-primary" />
          <div>
            <h2 className="text-sm font-semibold text-foreground">学习空间</h2>
            <p className="text-xs text-muted-foreground">{messageCountLabel}</p>
          </div>
        </div>
        {sending ? (
          <span className="text-xs text-muted-foreground">AI 正在思考...</span>
        ) : null}
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto px-6 py-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <BookOpen className="mb-4 size-12 text-muted-foreground/50" />
            <h3 className="text-lg font-medium text-foreground">
              开始你的学习之旅
            </h3>
            <p className="mt-2 max-w-md text-sm text-muted-foreground">
              告诉我你想学习什么，我会用费曼学习法、分块学习等科学方法来引导你
            </p>
          </div>
        ) : (
          messages.map((message) => {
            const isUser = message.role === "user";
            return (
              <div
                key={message.id}
                className={cn("flex", isUser ? "justify-end" : "justify-start")}
              >
                <div
                  className={cn(
                    "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm",
                    isUser
                      ? "bg-foreground text-background"
                      : "bg-muted text-foreground"
                  )}
                >
                  {isUser ? (
                    <p>{message.content}</p>
                  ) : (
                    <div className="prose prose-sm max-w-none text-foreground">
                      <ReactMarkdown>
                        {message.content || "..."}
                      </ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>

      {readonly ? null : (
        <div className="border-t px-6 py-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-end">
            <Textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={STEP_PLACEHOLDERS[currentStep]}
              className="min-h-[100px] md:flex-1"
              disabled={sending}
            />
            <Button
              type="button"
              onClick={onSendClick}
              className="md:w-32"
              disabled={sending || !input.trim()}
            >
              <SendHorizontal className="size-4" />
              发送
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
