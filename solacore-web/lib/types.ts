export type SolveStep =
  | "receive"
  | "clarify"
  | "reframe"
  | "options"
  | "commit";
export type SessionStatus = "active" | "completed" | "archived";

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  subscription_tier: "free" | "standard" | "pro";
  created_at: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  step?: SolveStep; // Optional to match backend
  emotion?: string;
  created_at: string;
}

export interface Session {
  id: string;
  current_step: SolveStep;
  status: SessionStatus;
  messages: Message[];
  created_at: string;
  completed_at?: string; // Renamed from updated_at to match backend
  first_message?: string; // First user message for list display
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
