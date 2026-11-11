import { useCallback, useEffect, useState } from 'react';
import {
  getLocaleFromDocument,
  getTranslation,
  subscribeToLocale,
  type Locale,
} from './locale';
import type { TranslationKey } from './types';

/** Return the active locale and a typed translation lookup function. */
export function useTranslations(): {
  locale: Locale;
  t: (key: TranslationKey) => string;
} {
  const [locale, setLocale] = useState<Locale>(getLocaleFromDocument);

  useEffect(() => subscribeToLocale(() => setLocale(getLocaleFromDocument())), []);

  const t = useCallback(
    (key: TranslationKey): string => getTranslation(locale, key),
    [locale],
  );

  return { locale, t };
}
