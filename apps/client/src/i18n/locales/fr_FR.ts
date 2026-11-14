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
    HOME_LINK: 'Accueil Mining Manager',
    PRIMARY_NAVIGATION: 'Navigation principale',
    IMAGE_UNAVAILABLE: '{alt} indisponible',
    PROFILE_MENU: 'Ouvrir le menu du profil',
    LANGUAGE: 'Langue',
    FRENCH_FLAG: 'Drapeau français',
    ENGLISH_FLAG: 'Drapeau anglais',
    PROFILE: 'Profil',
    LOGOUT: 'Se déconnecter',
  },
  TRANSACTIONS: {
    TITLE: 'Transactions',
    SIDEBAR_LABEL: 'Filtres des transactions',
    MATERIALS: 'Matériaux',
    RUNNING_TRANSACTIONS: 'Transactions en cours',
    ACTIVE_VIEW: 'Vue active : {view}',
    DESCRIPTION:
      'Sélectionnez une catégorie à gauche pour afficher les achats, ventes et éléments possédés dans cette même vue.',
    OWNED_ONLY: 'Afficher uniquement les objets possédés',
    QUANTITY_EXCEEDS_STOCK:
      'La quantité ne peut pas dépasser le stock disponible.',
    TT_EXCEEDS_BASE:
      'Le TT ne peut pas dépasser la valeur TT de base de l’objet.',
  },
  TRANSACTION_MODAL: {
    QUANTITY: 'Quantité',
    INSTANCE: 'Outil',
    AUTO_COMPUTE: 'Calcul automatique',
  },
  RUNNING_TRANSACTIONS_MODAL: {
    TITLE: 'Transactions en cours',
    TOOLS: 'Outils',
    RESOURCES: 'Ressources',
    NAME: 'Nom',
    QUANTITY: 'Quantité',
    CREATED_AT: 'Créée le',
    STATUS: 'Statut',
    LOADING: 'Chargement…',
    ERROR: 'Impossible de charger les transactions en cours.',
    EMPTY: 'Aucune transaction en cours.',
  },
  ITEM_STORE: {
    LOADING: 'Chargement des objets…',
    ERROR: 'Impossible de charger les objets.',
    EMPTY: 'Aucun objet trouvé.',
    NAME: 'Nom',
    DECAY: 'Dégradation',
    STOCK: 'Stock',
    BUY: 'Acheter',
    SELL: 'Vendre',
    FINANCIAL_SUMMARY: 'Résumé financier',
    TYPE: 'Type',
    BONUS: 'Bonus',
    EFFICIENCY: 'Efficacité',
    LEVEL_MIN: 'Niveau min.',
    DEPTH: 'Profondeur',
    RANGE: 'Portée',
    AMMO_BURN: 'Consommation de munitions',
    USE_PER_MINUTE: 'Utilisation / min',
  },
};
