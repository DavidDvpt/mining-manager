import type { TranslationSchema } from '../types';

export const en_EN: TranslationSchema = {
  AUTH: {
    SIGNIN: {
      TITLE: 'Sign in',
      SUBTITLE: 'Sign in to access Mining Manager.',
      PSEUDO: 'Username',
      PSEUDO_MIN_LENGTH: 'The username must contain at least 8 characters.',
      PSEUDO_MAX_LENGTH: 'The username cannot exceed 50 characters.',
      PASSWORD: 'Password',
      PASSWORD_MIN_LENGTH: 'The password must contain at least 8 characters.',
      PASSWORD_MAX_LENGTH: 'The password cannot exceed 50 characters.',
      SHOW_PASSWORD: 'Show password',
      HIDE_PASSWORD: 'Hide password',
      SUBMIT: 'Sign in',
      SUBMITTING: 'Signing in…',
    },
    SESSION: {
      CHECKING: 'Checking session…',
      LOADING: 'Loading session…',
    },
  },
  APP: {
    TITLE: 'Mining Manager',
    HOME_DESCRIPTION:
      'Find the main information about your activity here.',
  },
};
