import type { TranslationSchema } from '../types';

export const fr_FR: TranslationSchema = {
  AUTH: {
    SIGNIN: {
      TITLE: 'Connexion',
      SUBTITLE: 'Connectez-vous pour accéder à Mining Manager.',
      PSEUDO: 'Pseudo',
      PSEUDO_MIN_LENGTH: 'Le pseudo doit contenir au moins 8 caractères.',
      PSEUDO_MAX_LENGTH: 'Le pseudo ne peut pas dépasser 50 caractères.',
      PASSWORD: 'Mot de passe',
      PASSWORD_MIN_LENGTH:
        'Le mot de passe doit contenir au moins 8 caractères.',
      PASSWORD_MAX_LENGTH:
        'Le mot de passe ne peut pas dépasser 50 caractères.',
      SHOW_PASSWORD: 'Afficher le mot de passe',
      HIDE_PASSWORD: 'Masquer le mot de passe',
      SUBMIT: 'Se connecter',
      SUBMITTING: 'Connexion…',
    },
    SESSION: {
      CHECKING: 'Vérification de la session…',
      LOADING: 'Chargement de la session…',
    },
  },
  APP: {
    TITLE: 'Mining Manager',
    HOME_DESCRIPTION:
      'Retrouvez ici les informations principales de votre activité.',
  },
};
