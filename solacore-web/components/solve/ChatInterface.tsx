"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { SendHorizontal } from "lucide-react";
import { toast } from "sonner";

import type { Message, SolveStep } from "@/lib/types";
import { sendMessage } from "@/lib/session-api";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ChatInterfaceProps {
  sessionId: string;
  initialMessages?: Message[];
  currentStep?: SolveStep;
  readonly?: boolean;
  className?: string;
  onStreamComplete?: () => void;
}

const createLocalId = (): string => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `local-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

export function ChatInterface({
  sessionId,
  initialMessages = [],
  currentStep = "receive",
  readonly = false,
  className,
  onStreamComplete,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setMessages(initialMessages);
  }, [initialMessages, sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const messageCountLabel = useMemo(() => {
    return `${messages.length} 条消息`;
  }, [messages.length]);

  const handleSend = async () => {
    if (!input.trim() || sending || readonly) {
      return;
    }

    const trimmed = input.trim();
    const createdAt = new Date().toISOString();
    const userMessage: Message = {
      id: createLocalId(),
      role: "user",
      content: trimmed,
      step: currentStep,
      created_at: createdAt,
    };
    const assistantId = createLocalId();
    const assistantMessage: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      step: currentStep,
      created_at: createdAt,
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput("");
    setSending(true);

    let aggregated = "";

    try {
      const finalMessage = await sendMessage(sessionId, trimmed, {
        onToken: (token) => {
          aggregated += token;
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? { ...message, content: aggregated }
                : message,
            ),
          );
        },
        onMessage: (message) => {
          setMessages((prev) =>
            prev.map((item) => (item.id === assistantId ? message : item)),
          );
        },
      });

      if (finalMessage) {
        setMessages((prev) =>
          prev.map((item) => (item.id === assistantId ? finalMessage : item)),
        );
      }
    } catch (err) {
      setMessages((prev) => prev.filter((item) => item.id !== assistantId));
      toast.error(err instanceof Error ? err.message : "发送失败");
    } finally {
      setSending(false);
      onStreamComplete?.();
    }
  };

  return (
    <div
      className={cn(
        "flex h-full flex-col rounded-3xl border bg-card/80 shadow-sm",
        className,
      )}
    >
      <div className="flex items-center justify-between border-b px-6 py-4">
        <div>
          <h2 className="text-sm font-semibold text-foreground">对话空间</h2>
          <p className="text-xs text-muted-foreground">{messageCountLabel}</p>
        </div>
        {sending ? (
          <span className="text-xs text-muted-foreground">AI 正在思考...</span>
        ) : null}
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto px-6 py-6">
        {messages.map((message) => {
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
                    : "bg-muted text-foreground",
                )}
              >
                {isUser ? (
                  <p>{message.content}</p>
                ) : (
                  <div className="prose prose-sm max-w-none text-foreground">
                    <ReactMarkdown>{message.content || "..."}</ReactMarkdown>
                  </div>
                )}
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      {readonly ? null : (
        <div className="border-t px-6 py-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-end">
            <Textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="输入你的问题或感受..."
              className="min-h-[100px] md:flex-1"
              disabled={sending}
            />
            <Button
              type="button"
              onClick={handleSend}
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
