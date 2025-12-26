/**
 * 调试辅助工具 - 用于诊断 403 错误
 */

export const debugLog = (context: string, data: Record<string, unknown>) => {
  if (process.env.NODE_ENV === "development") {
    console.group(`🔍 [DEBUG] ${context}`);
    Object.entries(data).forEach(([key, value]) => {
      console.log(`  ${key}:`, value);
    });
    console.groupEnd();
  }
};

export const debugError = (context: string, error: unknown) => {
  if (process.env.NODE_ENV === "development") {
    console.error(`❌ [ERROR] ${context}`, error);
  }
};
