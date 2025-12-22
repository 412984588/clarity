/**
 * Step History Storage Service
 * Uses AsyncStorage to persist step history locally
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

import type { Message, SolveStep, StepHistoryEntry } from '../types/solve';

const HISTORY_PREFIX = 'step_history_';

/**
 * Get the storage key for a session
 */
const getStorageKey = (sessionId: string): string => {
  return `${HISTORY_PREFIX}${sessionId}`;
};

/**
 * Get step history for a session
 */
export const getStepHistory = async (sessionId: string): Promise<StepHistoryEntry[]> => {
  try {
    const data = await AsyncStorage.getItem(getStorageKey(sessionId));
    if (!data) {
      return [];
    }
    return JSON.parse(data) as StepHistoryEntry[];
  } catch {
    return [];
  }
};

/**
 * Save step history for a session
 */
export const saveStepHistory = async (
  sessionId: string,
  history: StepHistoryEntry[]
): Promise<void> => {
  try {
    await AsyncStorage.setItem(getStorageKey(sessionId), JSON.stringify(history));
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
  completed?: boolean
): Promise<void> => {
  const history = await getStepHistory(sessionId);
  const existingIndex = history.findIndex((entry) => entry.step === step);

  if (existingIndex >= 0) {
    // Update existing entry
    const entry = history[existingIndex];
    if (message) {
      entry.messages.push(message);
    }
    if (completed) {
      entry.completed_at = new Date().toISOString();
    }
  } else {
    // Create new entry
    const newEntry: StepHistoryEntry = {
      step,
      started_at: new Date().toISOString(),
      messages: message ? [message] : [],
    };
    if (completed) {
      newEntry.completed_at = new Date().toISOString();
    }
    history.push(newEntry);
  }

  await saveStepHistory(sessionId, history);
};

/**
 * Get all messages for a session (across all steps)
 */
export const getAllMessages = async (sessionId: string): Promise<Message[]> => {
  const history = await getStepHistory(sessionId);
  return history.flatMap((entry) => entry.messages);
};

/**
 * Clear step history for a session
 */
export const clearStepHistory = async (sessionId: string): Promise<void> => {
  try {
    await AsyncStorage.removeItem(getStorageKey(sessionId));
  } catch (error) {
    console.error('Failed to clear step history:', error);
  }
};

/**
 * Get all session IDs with stored history
 */
export const getAllSessionIds = async (): Promise<string[]> => {
  try {
    const keys = await AsyncStorage.getAllKeys();
    return keys
      .filter((key) => key.startsWith(HISTORY_PREFIX))
      .map((key) => key.slice(HISTORY_PREFIX.length));
  } catch {
    return [];
  }
};
