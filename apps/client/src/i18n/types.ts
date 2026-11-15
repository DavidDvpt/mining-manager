export type TranslationSchema = {
  AUTH: {
    SIGNIN: {
      TITLE: string;
      SUBTITLE: string;
      PSEUDO: string;
      PSEUDO_MIN_LENGTH: string;
      PSEUDO_MAX_LENGTH: string;
      PASSWORD: string;
      PASSWORD_MIN_LENGTH: string;
      PASSWORD_MAX_LENGTH: string;
      SHOW_PASSWORD: string;
      HIDE_PASSWORD: string;
      SUBMIT: string;
      SUBMITTING: string;
    };
    SESSION: {
      CHECKING: string;
      LOADING: string;
    };
  };
  APP: {
    TITLE: string;
    HOME_DESCRIPTION: string;
    HOME_LINK: string;
    PRIMARY_NAVIGATION: string;
    IMAGE_UNAVAILABLE: string;
    PROFILE_MENU: string;
    LANGUAGE: string;
    FRENCH_FLAG: string;
    ENGLISH_FLAG: string;
    PROFILE: string;
    LOGOUT: string;
  };
  TRANSACTIONS: {
    TITLE: string;
    SIDEBAR_LABEL: string;
    MATERIALS: string;
    RUNNING_TRANSACTIONS: string;
    ACTIVE_VIEW: string;
    DESCRIPTION: string;
    OWNED_ONLY: string;
    QUANTITY_EXCEEDS_STOCK: string;
    TT_EXCEEDS_BASE: string;
  };
  MINING: {
    TITLE: string;
    SIDEBAR_LABEL: string;
    LOOTS: string;
    COCKPIT: string;
    CREATE_SESSION: string;
    CREATE_SESSION_DESCRIPTION: string;
    CURRENT_SESSION: string;
    CLOSE: string;
    SESSIONS_LIST: string;
    ACTIVE_VIEW: string;
    DESCRIPTION: string;
  };
  TRANSACTION_MODAL: {
    QUANTITY: string;
    INSTANCE: string;
    AUTO_COMPUTE: string;
  };
  RUNNING_TRANSACTIONS_MODAL: {
    TITLE: string;
    TOOLS: string;
    RESOURCES: string;
    NAME: string;
    QUANTITY: string;
    CREATED_AT: string;
    STATUS: string;
    LOADING: string;
    ERROR: string;
    EMPTY: string;
  };
  ITEM_STORE: {
    LOADING: string;
    ERROR: string;
    EMPTY: string;
    NAME: string;
    DECAY: string;
    STOCK: string;
    BUY: string;
    SELL: string;
    EDIT: string;
    FINANCIAL_SUMMARY: string;
    TYPE: string;
    BONUS: string;
    EFFICIENCY: string;
    LEVEL_MIN: string;
    DEPTH: string;
    RANGE: string;
    AMMO_BURN: string;
    USE_PER_MINUTE: string;
  };
  TOOL_EDIT_MODAL: {
    TITLE: string;
    CANCEL: string;
    SAVE: string;
    SAVING: string;
    LOADING: string;
    ERROR: string;
  };
};

type StringKey<T> = Extract<keyof T, string>;

type TranslationPath<T> = {
  [Key in StringKey<T>]: T[Key] extends string
    ? Key
    : `${Key}.${TranslationPath<T[Key]>}`;
}[StringKey<T>];

export type TranslationKey = TranslationPath<TranslationSchema>;
