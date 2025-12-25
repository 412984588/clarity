/**
 * i18n 国际化模块
 * 使用 expo-localization 检测系统语言并加载对应翻译
 */

import * as Localization from 'expo-localization';

import en from './en.json';
import es from './es.json';
import zh from './zh.json';

export type SupportedLocale = 'en' | 'es' | 'zh';

type TranslationKeys = typeof en;

const translations: Record<SupportedLocale, TranslationKeys> = {
  en,
  es,
  zh,
};

/**
 * 获取系统首选语言的语言代码
 */
const getSystemLocale = (): SupportedLocale => {
  const locales = Localization.getLocales();
  if (locales.length === 0) {
    return 'en';
  }

  const languageCode = locales[0].languageCode?.toLowerCase() ?? 'en';

  // 支持的语言匹配
  if (languageCode === 'zh') {
    return 'zh';
  }
  if (languageCode === 'es') {
    return 'es';
  }

  // 默认英语
  return 'en';
};

let currentLocale: SupportedLocale = getSystemLocale();

/**
 * 获取当前语言
 */
export const getLocale = (): SupportedLocale => currentLocale;

/**
 * 设置当前语言（用于测试或手动切换）
 */
export const setLocale = (locale: SupportedLocale): void => {
  currentLocale = locale;
};

/**
 * 获取嵌套对象的值
 */
const getNestedValue = (obj: unknown, path: string): string | undefined => {
  const keys = path.split('.');
  let current: unknown = obj;

  for (const key of keys) {
    if (current === null || current === undefined) {
      return undefined;
    }
    if (typeof current !== 'object') {
      return undefined;
    }
    current = (current as Record<string, unknown>)[key];
  }

  return typeof current === 'string' ? current : undefined;
};

/**
 * 翻译函数
 * @param key - 点分隔的翻译键，如 "auth.welcomeBack"
 * @param params - 可选的插值参数
 */
export const t = (key: string, params?: Record<string, string | number>): string => {
  const translation = getNestedValue(translations[currentLocale], key);

  if (translation === undefined) {
    // 回退到英语
    const fallback = getNestedValue(translations.en, key);
    if (fallback === undefined) {
      // 开发时警告
      console.warn(`[i18n] Missing translation for key: ${key}`);
      return key;
    }
    return interpolate(fallback, params);
  }

  return interpolate(translation, params);
};

/**
 * 插值替换
 */
const interpolate = (text: string, params?: Record<string, string | number>): string => {
  if (!params) {
    return text;
  }

  return Object.entries(params).reduce((result, [key, value]) => {
    return result.replace(new RegExp(`\\{${key}\\}`, 'g'), String(value));
  }, text);
};

/**
 * React Hook 版本的翻译函数
 */
export const useI18n = () => {
  return {
    t,
    locale: currentLocale,
    setLocale,
  };
};

export default { t, getLocale, setLocale, useI18n };
