/**
 * Step History Storage Service
 * Uses SQLite for persistent local storage (upgraded from AsyncStorage)
 */

import type { Message, SolveStep, StepHistoryEntry } from '../types/solve';
import {
  initDatabase,
  insertMessage,
  getMessages,
  insertOption,
  getOptions,
  clearSessionData,
  isDatabaseInitialized,
  type Message as DbMessage,
} from './database';

/**
 * Ensure database is initialized before any operation
 */
const ensureDb = async (): Promise<void> => {
  if (!isDatabaseInitialized()) {
    await initDatabase();
  }
};

/**
 * Convert database message to app Message type
 */
const toAppMessage = (dbMsg: DbMessage, defaultStep: SolveStep = 'receive'): Message => ({
  id: dbMsg.id,
  role: dbMsg.role,
  content: dbMsg.content,
  step: (dbMsg.step as SolveStep) || defaultStep,
  timestamp: dbMsg.created_at ? new Date(dbMsg.created_at).toISOString() : new Date().toISOString(),
});

/**
 * Get step history for a session
 */
export const getStepHistory = async (sessionId: string): Promise<StepHistoryEntry[]> => {
  await ensureDb();

  try {
    const messages = await getMessages(sessionId);

    // Group messages by step
    const stepMap = new Map<SolveStep, StepHistoryEntry>();

    for (const msg of messages) {
      const step = (msg.step as SolveStep) || 'receive';

      if (!stepMap.has(step)) {
        stepMap.set(step, {
          step,
          started_at: msg.created_at ? new Date(msg.created_at).toISOString() : new Date().toISOString(),
          messages: [],
        });
      }

      stepMap.get(step)!.messages.push(toAppMessage(msg, step));
    }

    return Array.from(stepMap.values());
  } catch (error) {
    console.error('Failed to get step history:', error);
    return [];
  }
};

/**
 * Save step history for a session (batch insert)
 */
export const saveStepHistory = async (
  sessionId: string,
  history: StepHistoryEntry[]
): Promise<void> => {
  await ensureDb();

  try {
    // Clear existing data first
    await clearSessionData(sessionId);

    // Insert all messages
    for (const entry of history) {
      for (const msg of entry.messages) {
        await insertMessage({
          id: msg.id,
          session_id: sessionId,
          role: msg.role,
          content: msg.content,
          step: msg.step,
        });
      }
    }
  } catch (error) {
    console.error('Failed to save step history:', error);
  }
};

/**
 * Add or update a step entry in the history
 */
export const updateStepEntry = async (
  sessionId: string,
  step: SolveStep,
  message?: Message,
  _completed?: boolean
): Promise<void> => {
  await ensureDb();

  try {
    if (message) {
      await insertMessage({
        id: message.id,
        session_id: sessionId,
        role: message.role,
        content: message.content,
        step: step,
      });
    }
  } catch (error) {
    console.error('Failed to update step entry:', error);
  }
};

/**
 * Get all messages for a session (across all steps)
 */
export const getAllMessages = async (sessionId: string): Promise<Message[]> => {
  await ensureDb();

  try {
    const messages = await getMessages(sessionId);
    return messages.map((msg) => toAppMessage(msg));
  } catch (error) {
    console.error('Failed to get all messages:', error);
    return [];
  }
};

/**
 * Clear step history for a session
 */
export const clearStepHistory = async (sessionId: string): Promise<void> => {
  await ensureDb();

  try {
    await clearSessionData(sessionId);
  } catch (error) {
    console.error('Failed to clear step history:', error);
  }
};

/**
 * Get all session IDs with stored history
 * Note: This requires a custom query in SQLite
 */
export const getAllSessionIds = async (): Promise<string[]> => {
  await ensureDb();

  try {
    // For now, return empty - we'd need to add a dedicated function in database.ts
    // This is rarely used and can be implemented if needed
    return [];
  } catch {
    return [];
  }
};

// Re-export option functions for direct use
export { insertOption, getOptions };
