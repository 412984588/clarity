/**
 * Solve 5-Step Flow Types
 */

export type SolveStep = 'receive' | 'clarify' | 'reframe' | 'options' | 'commit';

export type SessionStatus = 'active' | 'completed' | 'abandoned';

export interface SolveSession {
  session_id: string;
  status: SessionStatus;
  current_step: SolveStep;
  created_at: string;
  usage?: {
    sessions_used: number;
    sessions_limit: number;
    tier: string;
  };
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  step: SolveStep;
  timestamp: string;
}

export interface StepHistoryEntry {
  step: SolveStep;
  started_at: string;
  completed_at?: string;
  messages: Message[];
}

export interface CrisisResponse {
  blocked: true;
  reason: 'CRISIS';
  resources: {
    US: string;
    ES: string;
  };
  message?: string;
}

export interface StreamDoneEvent {
  next_step?: SolveStep;
  emotion_detected?: string;
}

export interface SessionPatchRequest {
  status?: SessionStatus;
  current_step?: SolveStep;
  locale?: string;
  first_step_action?: string;
  reminder_time?: string;
}

export interface SessionPatchResponse {
  id: string;
  status: SessionStatus;
  current_step: SolveStep;
  updated_at: string;
}

// Step metadata for UI
export const SOLVE_STEPS: { key: SolveStep; labelKey: string }[] = [
  { key: 'receive', labelKey: 'solve.stepReceive' },
  { key: 'clarify', labelKey: 'solve.stepClarify' },
  { key: 'reframe', labelKey: 'solve.stepReframe' },
  { key: 'options', labelKey: 'solve.stepOptions' },
  { key: 'commit', labelKey: 'solve.stepCommit' },
];

export const getStepIndex = (step: SolveStep): number => {
  return SOLVE_STEPS.findIndex((s) => s.key === step);
};
