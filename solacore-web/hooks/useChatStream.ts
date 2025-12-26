import { useState, useCallback } from "react";
import { toast } from "sonner";

import type { Message, SolveStep } from "@/lib/types";
import { sendMessage } from "@/lib/session-api";

const createLocalId = (): string => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `local-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

interface UseChatStreamOptions {
  sessionId: string;
  currentStep: SolveStep;
  onStreamComplete?: () => void;
}

interface UseChatStreamReturn {
  messages: Message[];
  sending: boolean;
  handleSend: (input: string) => Promise<void>;
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

export function useChatStream({
  sessionId,
  currentStep,
  onStreamComplete,
}: UseChatStreamOptions): UseChatStreamReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sending, setSending] = useState(false);

  const handleSend = useCallback(
    async (input: string) => {
      if (!input.trim() || sending) {
        return;
      }

      // 防护：确保 sessionId 有效
      if (!sessionId) {
        toast.error("会话未就绪，请刷新页面重试");
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
      setSending(true);

      let aggregated = "";

      try {
        const finalMessage = await sendMessage(
          sessionId,
          trimmed,
          currentStep,
          {
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
          },
        );

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
    },
    [sessionId, currentStep, sending, onStreamComplete],
  );

  return {
    messages,
    sending,
    handleSend,
    setMessages,
  };
}
