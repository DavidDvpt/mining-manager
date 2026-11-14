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
    HOME_LINK: 'Mining Manager home',
    PRIMARY_NAVIGATION: 'Main navigation',
    IMAGE_UNAVAILABLE: '{alt} unavailable',
    PROFILE_MENU: 'Open profile menu',
    PROFILE: 'Profile',
    LOGOUT: 'Log out',
  },
  TRANSACTIONS: {
    TITLE: 'Transactions',
    SIDEBAR_LABEL: 'Transaction filters',
    MATERIALS: 'Materials',
    RUNNING_TRANSACTIONS: 'Running transactions',
    ACTIVE_VIEW: 'Active view: {view}',
    DESCRIPTION:
      'Select a category on the left to display purchases, sales, and owned items in the same view.',
    QUANTITY_EXCEEDS_STOCK: 'The quantity cannot exceed available stock.',
    TT_EXCEEDS_BASE: 'The TT cannot exceed the item base TT value.',
  },
  TRANSACTION_MODAL: {
    QUANTITY: 'Quantity',
    AUTO_COMPUTE: 'Automatic calculation',
  },
  ITEM_STORE: {
    LOADING: 'Loading items…',
    ERROR: 'Unable to load items.',
    EMPTY: 'No items found.',
    NAME: 'Name',
    DECAY: 'Decay',
    STOCK: 'Stock',
    BUY: 'Buy',
    SELL: 'Sell',
    FINANCIAL_SUMMARY: 'Financial summary',
    TYPE: 'Type',
    BONUS: 'Bonus',
    EFFICIENCY: 'Efficiency',
    LEVEL_MIN: 'Min. level',
    DEPTH: 'Depth',
    RANGE: 'Range',
    AMMO_BURN: 'Ammo burn',
    USE_PER_MINUTE: 'Use / min',
  },
};
