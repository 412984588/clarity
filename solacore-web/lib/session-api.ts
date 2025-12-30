import type { Message, Session, SolveStep } from "@/lib/types";
import { api, getDeviceFingerprint } from "@/lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface StreamHandlers {
  onToken?: (token: string) => void;
  onMessage?: (message: Message) => void;
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

// 后端 SessionCreateResponse 返回 session_id，需要映射到 id
interface CreateSessionResponse {
  session_id: string;
  status: string;
  current_step: string;
  created_at: string;
  usage: {
    sessions_used: number;
    sessions_limit: number;
    tier: string;
  };
}

export const createSession = async (): Promise<Session> => {
  if (process.env.NODE_ENV === "development") {
    console.log("🆕 [Create Session] 开始创建会话", {
      fingerprint: getDeviceFingerprint(),
      timestamp: new Date().toISOString(),
    });
  }

  const response = await api.post<CreateSessionResponse>("/sessions");

  // 映射后端字段到前端 Session 类型
  const session: Session = {
    id: response.data.session_id,
    status: response.data.status as Session["status"],
    current_step: response.data.current_step as Session["current_step"],
    created_at: response.data.created_at,
    messages: [], // 新创建的会话没有消息
  };

  if (process.env.NODE_ENV === "development") {
    console.log("✅ [Create Session] 会话创建成功", {
      sessionId: session.id,
    });
  }

  return session;
};

export const getSession = async (id: string): Promise<Session> => {
  // 添加 include_messages=true 以获取会话消息历史
  const response = await api.get<Session>(`/sessions/${id}?include_messages=true`);
  return response.data;
};

export const listSessions = async (): Promise<Session[]> => {
  const response = await api.get<{ sessions: Session[] }>("/sessions");
  // 后端返回 { sessions: [], total: 0, limit: 20, offset: 0 }
  return response.data.sessions;
};

export const updateStep = async (
  id: string,
  step: SolveStep,
): Promise<Session> => {
  const response = await api.patch<Session>(`/sessions/${id}`, {
    step,
    current_step: step,
  });
  return response.data;
};

export const sendMessage = async (
  id: string,
  content: string,
  step: string, // 后端要求必传 step 字段
  handlers: StreamHandlers = {},
): Promise<Message | null> => {
  const fingerprint = getDeviceFingerprint();

  if (process.env.NODE_ENV === "development") {
    console.log("💬 [Send Message] 发送消息", {
      sessionId: id,
      step,
      fingerprint,
      contentLength: content.length,
      timestamp: new Date().toISOString(),
    });
  }

  // 🔧 修复：手动添加设备指纹到请求头（因为使用原生 fetch，不经过 axios 拦截器）
  const response = await fetch(`${API_BASE_URL}/sessions/${id}/messages`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      "X-Device-Fingerprint": fingerprint, // ✅ 添加设备指纹
    },
    credentials: "include", // httpOnly cookies 模式：自动发送 cookies
    body: JSON.stringify({ content, step }), // ✅ 添加 step 字段
    signal: handlers.signal,
  });

  if (!response.ok) {
    if (process.env.NODE_ENV === "development") {
      console.error("❌ [Send Message] 请求失败", {
        status: response.status,
        statusText: response.statusText,
        fingerprint,
      });
    }
    throw new Error("Failed to send message");
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("text/event-stream") || !response.body) {
    const message = (await response.json()) as Message;
    return message;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let aggregated = "";
  let finalMessage: Message | null = null;
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

      if (payload && typeof payload === "object") {
        const maybeMessage = (payload as { message?: Message }).message;
        if (maybeMessage) {
          finalMessage = maybeMessage;
          handlers.onMessage?.(maybeMessage);
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
    const message: Message = {
      id: createLocalId(),
      role: "assistant",
      content: aggregated,
      step: "receive",
      created_at: new Date().toISOString(),
    };
    handlers.onMessage?.(message);
    return message;
  }

  return null;
};

export const deleteSession = async (id: string): Promise<void> => {
  if (process.env.NODE_ENV === "development") {
    console.log("🗑️ [Delete Session] 删除会话", {
      sessionId: id,
      timestamp: new Date().toISOString(),
    });
  }

  await api.delete(`/sessions/${id}`);

  if (process.env.NODE_ENV === "development") {
    console.log("✅ [Delete Session] 会话删除成功", {
      sessionId: id,
    });
  }
};
