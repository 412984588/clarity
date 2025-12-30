import type { LearnMessage, LearnSession, LearnStep } from "@/lib/types";
import { api, getDeviceFingerprint } from "@/lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface StreamHandlers {
  onToken?: (token: string) => void;
  onMessage?: (message: LearnMessage) => void;
  onDone?: (data: {
    message_id: string;
    next_step: LearnStep | null;
    step_completed: boolean;
    session_completed: boolean;
  }) => void;
  signal?: AbortSignal;
}

const createLocalId = (): string => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `local-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

const resolveToken = (payload: unknown): string | null => {
  if (typeof payload === "string") {
    return payload;
  }

  if (payload && typeof payload === "object") {
    const data = payload as {
      content?: string;
      delta?: string;
      token?: string;
      text?: string;
    };
    return data.content ?? data.delta ?? data.token ?? data.text ?? null;
  }

  return null;
};

// 后端返回的创建会话响应
interface CreateLearnSessionResponse {
  session_id: string;
  status: string;
  current_step: string;
  created_at: string;
}

export const createLearnSession = async (): Promise<LearnSession> => {
  if (process.env.NODE_ENV === "development") {
    console.log("🎓 [Create Learn Session] 开始创建学习会话", {
      fingerprint: getDeviceFingerprint(),
      timestamp: new Date().toISOString(),
    });
  }

  const response = await api.post<CreateLearnSessionResponse>("/learn");

  const session: LearnSession = {
    id: response.data.session_id,
    status: response.data.status as LearnSession["status"],
    current_step: response.data.current_step as LearnSession["current_step"],
    created_at: response.data.created_at,
    messages: [],
  };

  if (process.env.NODE_ENV === "development") {
    console.log("✅ [Create Learn Session] 学习会话创建成功", {
      sessionId: session.id,
    });
  }

  return session;
};

export const getLearnSession = async (id: string): Promise<LearnSession> => {
  const response = await api.get<LearnSession>(`/learn/${id}`);
  return response.data;
};

export const listLearnSessions = async (): Promise<LearnSession[]> => {
  const response = await api.get<{ sessions: LearnSession[] }>("/learn");
  return response.data.sessions;
};

export const updateLearnStep = async (
  id: string,
  step: LearnStep
): Promise<LearnSession> => {
  const response = await api.patch<LearnSession>(`/learn/${id}`, {
    current_step: step,
  });
  return response.data;
};

export const sendLearnMessage = async (
  id: string,
  content: string,
  step: string,
  handlers: StreamHandlers = {}
): Promise<LearnMessage | null> => {
  const fingerprint = getDeviceFingerprint();

  if (process.env.NODE_ENV === "development") {
    console.log("📚 [Send Learn Message] 发送学习消息", {
      sessionId: id,
      step,
      fingerprint,
      contentLength: content.length,
      timestamp: new Date().toISOString(),
    });
  }

  const response = await fetch(`${API_BASE_URL}/learn/${id}/messages`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      "X-Device-Fingerprint": fingerprint,
    },
    credentials: "include",
    body: JSON.stringify({ content, step }),
    signal: handlers.signal,
  });

  if (!response.ok) {
    if (process.env.NODE_ENV === "development") {
      console.error("❌ [Send Learn Message] 请求失败", {
        status: response.status,
        statusText: response.statusText,
        fingerprint,
      });
    }
    throw new Error("Failed to send learn message");
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("text/event-stream") || !response.body) {
    const message = (await response.json()) as LearnMessage;
    return message;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let aggregated = "";
  const finalMessage: LearnMessage | null = null;
  let shouldStop = false;

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed.startsWith("data:")) {
        continue;
      }

      const payloadText = trimmed.replace(/^data:\s*/, "").trim();
      if (!payloadText) {
        continue;
      }

      if (payloadText === "[DONE]") {
        shouldStop = true;
        break;
      }

      let payload: unknown = payloadText;
      try {
        payload = JSON.parse(payloadText) as unknown;
      } catch {
        payload = payloadText;
      }

      // 处理 done 事件
      if (payload && typeof payload === "object") {
        const data = payload as {
          message_id?: string;
          next_step?: string | null;
          step_completed?: boolean;
          session_completed?: boolean;
        };
        if (data.message_id) {
          handlers.onDone?.({
            message_id: data.message_id,
            next_step: data.next_step as LearnStep | null,
            step_completed: data.step_completed ?? false,
            session_completed: data.session_completed ?? false,
          });
        }
      }

      const token = resolveToken(payload);
      if (token) {
        aggregated += token;
        handlers.onToken?.(token);
      }
    }

    if (shouldStop) {
      break;
    }
  }

  if (finalMessage) {
    return finalMessage;
  }

  if (aggregated) {
    const message: LearnMessage = {
      id: createLocalId(),
      role: "assistant",
      content: aggregated,
      step: step as LearnStep,
      created_at: new Date().toISOString(),
    };
    handlers.onMessage?.(message);
    return message;
  }

  return null;
};

export const deleteLearnSession = async (id: string): Promise<void> => {
  if (process.env.NODE_ENV === "development") {
    console.log("🗑️ [Delete Learn Session] 删除学习会话", {
      sessionId: id,
      timestamp: new Date().toISOString(),
    });
  }

  await api.delete(`/learn/${id}`);

  if (process.env.NODE_ENV === "development") {
    console.log("✅ [Delete Learn Session] 学习会话删除成功", {
      sessionId: id,
    });
  }
};
