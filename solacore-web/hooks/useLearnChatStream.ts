import { useState, useCallback } from "react";
import { toast } from "sonner";

import type { LearnMessage, LearnStep } from "@/lib/types";
import { sendLearnMessage } from "@/lib/learn-api";

const createLocalId = (): string => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `local-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

interface UseLearnChatStreamOptions {
  sessionId: string;
  currentStep: LearnStep;
  onStreamComplete?: () => void;
  onStepComplete?: (nextStep: LearnStep | null) => void;
  onSessionComplete?: () => void;
}

interface UseLearnChatStreamReturn {
  messages: LearnMessage[];
  sending: boolean;
  handleSend: (input: string) => Promise<void>;
  setMessages: React.Dispatch<React.SetStateAction<LearnMessage[]>>;
}

export function useLearnChatStream({
  sessionId,
  currentStep,
  onStreamComplete,
  onStepComplete,
  onSessionComplete,
}: UseLearnChatStreamOptions): UseLearnChatStreamReturn {
  const [messages, setMessages] = useState<LearnMessage[]>([]);
  const [sending, setSending] = useState(false);

  const handleSend = useCallback(
    async (input: string) => {
      if (!input.trim() || sending) {
        return;
      }

      if (!sessionId) {
        toast.error("学习会话未就绪，请刷新页面重试");
        return;
      }

      const trimmed = input.trim();
      const createdAt = new Date().toISOString();
      const userMessage: LearnMessage = {
        id: createLocalId(),
        role: "user",
        content: trimmed,
        step: currentStep,
        created_at: createdAt,
      };
      const assistantId = createLocalId();
      const assistantMessage: LearnMessage = {
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
        const finalMessage = await sendLearnMessage(
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
                    : message
                )
              );
            },
            onMessage: (message) => {
              setMessages((prev) =>
                prev.map((item) => (item.id === assistantId ? message : item))
              );
            },
            onDone: (data) => {
              if (data.session_completed) {
                onSessionComplete?.();
              } else if (data.step_completed && data.next_step) {
                onStepComplete?.(data.next_step);
              }
            },
          }
        );

        if (finalMessage) {
          setMessages((prev) =>
            prev.map((item) => (item.id === assistantId ? finalMessage : item))
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
    [sessionId, currentStep, sending, onStreamComplete, onStepComplete, onSessionComplete]
  );

  return {
    messages,
    sending,
    handleSend,
    setMessages,
  };
}
