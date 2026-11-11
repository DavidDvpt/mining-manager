import { z } from 'zod';
import type { TranslationKey } from '../../i18n/types';

type Translate = (key: TranslationKey) => string;

/** Build the signin validation schema with messages from the active locale. */
export function createSignInSchema(t: Translate) {
  return z.object({
    pseudo: z
      .string()
      .min(8, t('AUTH.SIGNIN.PSEUDO_MIN_LENGTH'))
      .max(50, t('AUTH.SIGNIN.PSEUDO_MAX_LENGTH')),
    password: z
      .string()
      .min(8, t('AUTH.SIGNIN.PASSWORD_MIN_LENGTH'))
      .max(50, t('AUTH.SIGNIN.PASSWORD_MAX_LENGTH')),
  });
}

export type SignInValues = z.infer<ReturnType<typeof createSignInSchema>>;
