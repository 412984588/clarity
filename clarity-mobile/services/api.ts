import { clearTokens, getTokens, saveTokens } from './auth';
import { API_URL } from './config';

type ApiRequestOptions = {
  method?: string;
  headers?: Record<string, string>;
  body?: unknown;
  auth?: boolean;
};

export type ApiError = {
  status: number;
  message: string;
  details?: unknown;
};

const buildHeaders = async (auth: boolean, extra?: Record<string, string>): Promise<Record<string, string>> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...extra,
  };

  if (auth) {
    const { accessToken } = await getTokens();
    if (accessToken) {
      headers.Authorization = `Bearer ${accessToken}`;
    }
  }

  return headers;
};

const parseJson = async <T>(response: Response): Promise<T | null> => {
  const text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
};

type ErrorPayload = {
  message?: string;
  detail?: unknown;
};

const createApiError = async (response: Response): Promise<ApiError> => {
  const payload = await parseJson<ErrorPayload>(response);
  let message = response.statusText ?? 'Request failed';

  if (payload) {
    if (typeof payload.message === 'string') {
      message = payload.message;
    } else if (typeof payload.detail === 'string') {
      message = payload.detail;
    } else if (Array.isArray(payload.detail)) {
      const first = payload.detail[0] as { msg?: string; message?: string } | undefined;
      if (first?.msg) {
        message = String(first.msg);
      } else if (first?.message) {
        message = String(first.message);
      }
    }
  }

  return {
    status: response.status,
    message,
    details: payload,
  };
};

export const refreshTokens = async (): Promise<{ access_token: string; refresh_token: string }> => {
  const { refreshToken } = await getTokens();
  if (!refreshToken) {
    throw new Error('Missing refresh token');
  }

  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    await clearTokens();
    throw await createApiError(response);
  }

  const data = (await parseJson<{ access_token: string; refresh_token: string }>(response)) ?? {
    access_token: '',
    refresh_token: '',
  };

  await saveTokens(data.access_token, data.refresh_token);
  return data;
};

export const apiRequest = async <T>(
  path: string,
  options: ApiRequestOptions = {},
  hasRetried = false
): Promise<T> => {
  const auth = options.auth ?? true;
  const headers = await buildHeaders(auth, options.headers);

  const response = await fetch(`${API_URL}${path}`, {
    method: options.method ?? 'GET',
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  if (response.status === 401 && auth && !hasRetried) {
    try {
      await refreshTokens();
      return apiRequest<T>(path, options, true);
    } catch (error) {
      throw error;
    }
  }

  if (!response.ok) {
    throw await createApiError(response);
  }

  const data = await parseJson<T>(response);
  return (data ?? ({} as T)) as T;
};
