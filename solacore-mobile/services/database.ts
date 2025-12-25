/**
 * SQLite 本地数据库服务
 *
 * 用于存储聊天消息和选项，支持离线访问和快速历史加载
 */
import * as SQLite from 'expo-sqlite';

const DB_NAME = 'solacore.db';

// 表结构 - 消息和选项
const SCHEMA = `
  CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    step TEXT,
    emotion TEXT,
    created_at INTEGER NOT NULL
  );

  CREATE TABLE IF NOT EXISTS options (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    content TEXT NOT NULL,
    is_selected INTEGER DEFAULT 0,
    created_at INTEGER NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
  CREATE INDEX IF NOT EXISTS idx_options_session ON options(session_id);
`;

let db: SQLite.SQLiteDatabase | null = null;

/**
 * 初始化数据库
 * 在 app 启动时调用一次
 */
export const initDatabase = async (): Promise<void> => {
  try {
    db = await SQLite.openDatabaseAsync(DB_NAME);
    await db.execAsync(SCHEMA);
    console.log('SQLite 数据库初始化成功');
  } catch (error) {
    console.error('SQLite 初始化失败', error);
    throw error;
  }
};

/**
 * 获取数据库实例（内部使用）
 */
const getDb = (): SQLite.SQLiteDatabase => {
  if (!db) throw new Error('Database not initialized');
  return db;
};

// ============ 消息相关操作 ============

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  step?: string;
  emotion?: string;
  created_at?: number;
}

/**
 * 插入一条消息
 */
export const insertMessage = async (message: Omit<Message, 'created_at'>): Promise<void> => {
  const database = getDb();
  await database.runAsync(
    `INSERT OR REPLACE INTO messages (id, session_id, role, content, step, emotion, created_at)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
    [
      message.id,
      message.session_id,
      message.role,
      message.content,
      message.step || null,
      message.emotion || null,
      Date.now(),
    ]
  );
};

/**
 * 批量插入消息
 */
export const insertMessages = async (messages: Omit<Message, 'created_at'>[]): Promise<void> => {
  const database = getDb();
  for (const message of messages) {
    await database.runAsync(
      `INSERT OR REPLACE INTO messages (id, session_id, role, content, step, emotion, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [
        message.id,
        message.session_id,
        message.role,
        message.content,
        message.step || null,
        message.emotion || null,
        Date.now(),
      ]
    );
  }
};

/**
 * 获取某个 session 的所有消息（按时间升序）
 */
export const getMessages = async (sessionId: string): Promise<Message[]> => {
  const database = getDb();
  const result = await database.getAllAsync<Message>(
    'SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC',
    [sessionId]
  );
  return result;
};

/**
 * 获取某个 session 的最新 N 条消息
 */
export const getRecentMessages = async (
  sessionId: string,
  limit: number = 50
): Promise<Message[]> => {
  const database = getDb();
  const result = await database.getAllAsync<Message>(
    'SELECT * FROM messages WHERE session_id = ? ORDER BY created_at DESC LIMIT ?',
    [sessionId, limit]
  );
  return result.reverse(); // 反转为升序
};

// ============ 选项相关操作 ============

export interface Option {
  id: string;
  session_id: string;
  content: string;
  is_selected?: number;
  created_at?: number;
}

/**
 * 插入一个选项
 */
export const insertOption = async (
  option: Omit<Option, 'is_selected' | 'created_at'>
): Promise<void> => {
  const database = getDb();
  await database.runAsync(
    `INSERT OR REPLACE INTO options (id, session_id, content, created_at)
     VALUES (?, ?, ?, ?)`,
    [option.id, option.session_id, option.content, Date.now()]
  );
};

/**
 * 批量插入选项
 */
export const insertOptions = async (
  options: Omit<Option, 'is_selected' | 'created_at'>[]
): Promise<void> => {
  const database = getDb();
  for (const option of options) {
    await database.runAsync(
      `INSERT OR REPLACE INTO options (id, session_id, content, created_at)
       VALUES (?, ?, ?, ?)`,
      [option.id, option.session_id, option.content, Date.now()]
    );
  }
};

/**
 * 获取某个 session 的所有选项
 */
export const getOptions = async (sessionId: string): Promise<Option[]> => {
  const database = getDb();
  const result = await database.getAllAsync<Option>(
    'SELECT * FROM options WHERE session_id = ? ORDER BY created_at ASC',
    [sessionId]
  );
  return result;
};

/**
 * 标记选项为已选择
 */
export const updateOptionSelected = async (optionId: string): Promise<void> => {
  const database = getDb();
  await database.runAsync('UPDATE options SET is_selected = 1 WHERE id = ?', [optionId]);
};

// ============ 清理操作 ============

/**
 * 清除某个 session 的所有数据
 */
export const clearSessionData = async (sessionId: string): Promise<void> => {
  const database = getDb();
  await database.runAsync('DELETE FROM messages WHERE session_id = ?', [sessionId]);
  await database.runAsync('DELETE FROM options WHERE session_id = ?', [sessionId]);
};

/**
 * 清除所有数据（谨慎使用）
 */
export const clearAllData = async (): Promise<void> => {
  const database = getDb();
  await database.runAsync('DELETE FROM messages');
  await database.runAsync('DELETE FROM options');
};

/**
 * 检查数据库是否已初始化
 */
export const isDatabaseInitialized = (): boolean => {
  return db !== null;
};
