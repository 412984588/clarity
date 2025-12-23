/**
 * Solve Session Service
 * Handles session creation, SSE streaming, and session updates
 */

import { getDeviceFingerprint, getTokens } from './auth';
import { API_URL } from './config';

import type {
  SolveSession,
  SolveStep,
  CrisisResponse,
  StreamDoneEvent,
  SessionPatchRequest,
  SessionPatchResponse,
} from '../types/solve';

/**
 * Create a new solve session
 */
export const createSession = async (): Promise<SolveSession> => {
  const { accessToken } = await getTokens();
  const deviceFingerprint = await getDeviceFingerprint();

  const response = await fetch(`${API_URL}/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
      'X-Device-Fingerprint': deviceFingerprint,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail ?? errorData.message ?? 'Failed to create session');
  }

  return response.json();
};

/**
 * SSE streaming callback types
 */
export interface StreamCallbacks {
  onToken: (content: string) => void;
  onDone: (data: StreamDoneEvent) => void;
  onCrisis: (data: CrisisResponse) => void;
  onError: (error: Error) => void;
}

const handleSseData = (dataStr: string, callbacks: StreamCallbacks): boolean => {
  if (!dataStr || dataStr === '[DONE]') {
    return false;
  }

  try {
    const data = JSON.parse(dataStr);

    if (data?.blocked && data?.reason === 'CRISIS') {
      callbacks.onCrisis(data as CrisisResponse);
      return true;
    }

    if (data?.content !== undefined) {
      callbacks.onToken(data.content);
    }

    if (data?.next_step !== undefined || data?.emotion_detected !== undefined) {
      callbacks.onDone(data as StreamDoneEvent);
    }
  } catch {
    return false;
  }

  return false;
};

const parseSseText = (text: string, callbacks: StreamCallbacks): boolean => {
  const lines = text.split('\n');
  let handled = false;
  for (const line of lines) {
    if (line.startsWith('event: ')) {
      continue;
    }

    if (line.startsWith('data: ')) {
      handled = true;
      const shouldStop = handleSseData(line.slice(6), callbacks);
      if (shouldStop) {
        return true;
      }
    }
  }

  return handled;
};

/**
 * Send a message to the session and stream the response
 * Uses SSE (Server-Sent Events) for real-time streaming
 */
export const streamMessage = async (
  sessionId: string,
  content: string,
  step: SolveStep,
  callbacks: StreamCallbacks
): Promise<void> => {
  const { accessToken } = await getTokens();

  const response = await fetch(`${API_URL}/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({ content, step }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));

    // Check for crisis response
    if (errorData.blocked && errorData.reason === 'CRISIS') {
      callbacks.onCrisis(errorData as CrisisResponse);
      return;
    }

    callbacks.onError(new Error(errorData.detail ?? errorData.message ?? 'Failed to send message'));
    return;
  }

  // Check content type for crisis response (non-SSE)
  const contentType = response.headers.get('content-type');
  if (contentType?.includes('application/json')) {
    const data = await response.json();
    if (data.blocked && data.reason === 'CRISIS') {
      callbacks.onCrisis(data as CrisisResponse);
      return;
    }
  }

  // Handle SSE stream
  const reader = response.body?.getReader?.();
  if (!reader) {
    const text = await response.text();
    if (!text) {
      callbacks.onError(new Error('Empty response body'));
      return;
    }
    const handled = parseSseText(text, callbacks);
    if (!handled) {
      callbacks.onError(new Error('Stream not supported'));
    }
    return;
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    let reading = true;
    while (reading) {
      const { done, value } = await reader.read();
      if (done) {
        reading = false;
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        // Skip event type lines
        if (line.startsWith('event: ')) {
          continue;
        }

        if (line.startsWith('data: ')) {
          const shouldStop = handleSseData(line.slice(6), callbacks);
          if (shouldStop) {
            return;
          }
        }
      }
    }
  } catch (error) {
    callbacks.onError(error instanceof Error ? error : new Error('Stream error'));
  } finally {
    reader.releaseLock();
  }
};

/**
 * Update session (PATCH)
 * Used for updating first_step_action, reminder_time, status, etc.
 */
export const patchSession = async (
  sessionId: string,
  updates: SessionPatchRequest
): Promise<SessionPatchResponse> => {
  const { accessToken } = await getTokens();

  const response = await fetch(`${API_URL}/sessions/${sessionId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(updates),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail ?? errorData.message ?? 'Failed to update session');
  }

  return response.json();
};
