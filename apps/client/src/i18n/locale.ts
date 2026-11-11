import { en_EN } from './locales/en_EN';
import { fr_FR } from './locales/fr_FR';
import type { TranslationKey, TranslationSchema } from './types';

export const DEFAULT_LOCALE = 'en_EN' as const;
export type Locale = typeof DEFAULT_LOCALE | 'fr_FR';

const localeTranslations: Record<Locale, TranslationSchema> = {
  en_EN,
  fr_FR,
};

const LANGUAGE_CHANGE_EVENT = 'mining-manager:languagechange';

/** Resolve the application locale from the document language attribute. */
export function getLocaleFromDocument(): Locale {
  if (typeof document === 'undefined') {
    return DEFAULT_LOCALE;
  }

  return document.documentElement.lang.toLowerCase().startsWith('fr')
    ? 'fr_FR'
    : DEFAULT_LOCALE;
}

/** Return the translation table for a resolved locale. */
export function getTranslations(locale: Locale): TranslationSchema {
  return localeTranslations[locale] ?? localeTranslations[DEFAULT_LOCALE];
}

/** Resolve a dot-separated translation path from a nested locale dictionary. */
export function getTranslation(locale: Locale, key: TranslationKey): string {
  const value = key.split('.').reduce<unknown>(
    (current, segment) =>
      current && typeof current === 'object'
        ? (current as Record<string, unknown>)[segment]
        : undefined,
    getTranslations(locale),
  );

  if (typeof value === 'string') {
    return value;
  }

  const fallbackValue = key.split('.').reduce<unknown>(
    (current, segment) =>
      current && typeof current === 'object'
        ? (current as Record<string, unknown>)[segment]
        : undefined,
    en_EN,
  );

  return typeof fallbackValue === 'string' ? fallbackValue : key;
}

/** Update the HTML language tag and notify mounted translation consumers. */
export function setDocumentLocale(locale: Locale): void {
  if (typeof document === 'undefined') {
    return;
  }

  document.documentElement.lang = locale === 'fr_FR' ? 'fr-FR' : 'en-US';
  document.dispatchEvent(new Event(LANGUAGE_CHANGE_EVENT));
}

/** Subscribe to language changes made by the future language selector. */
export function subscribeToLocale(listener: () => void): () => void {
  document.addEventListener(LANGUAGE_CHANGE_EVENT, listener);
  return () => document.removeEventListener(LANGUAGE_CHANGE_EVENT, listener);
}
