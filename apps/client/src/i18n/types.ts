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
    SETUP: {
      TITLE: string;
      SEARCH_SETUP: string;
      ADD_FINDER: string;
      REMOVE_FINDER: string;
      FINDER_DEPTH: string;
      FINDER_DECAY: string;
      CHOOSE_FINDER: string;
      EXCAVATORS: string;
      REPAIRABLE: string;
      CLOSING_COST: string;
      NO_TOOLS: string;
      AMMO: string;
      AMP_MODEL: string;
      NO_AMP: string;
      AMP_REQUIRES_FINDER: string;
      AVAILABLE: string;
      CLICKS: string;
      SESSION_COST: string;
      AMP_INSUFFICIENT_QUANTITY: string;
      COMMON_TIER: string;
      DEFERRED_USAGE: string;
      UNIT_COST: string;
      NO_SOCKETS: string;
      ESTIMATE: string;
      DEFERRED_COST: string;
      LOADING: string;
      LOAD_ERROR: string;
      SUBMIT: string;
      INVALID_FINDERS: string;
      INCOMPLETE_FINDER: string;
      FINDER_CAPACITY: string;
      INVALID_EXCAVATORS: string;
      AMP_CAPACITY: string;
      INVALID_ENHANCER: string;
    };
    TITLE: string;
    SIDEBAR_LABEL: string;
    LOOTS: string;
    COCKPIT: string;
    CREATE_SESSION: string;
    CREATE_SESSION_DESCRIPTION: string;
    BASE: string;
    CLICKS: string;
    SEARCH_TYPE: string;
    ENMATTER: string;
    ORE: string;
    ORE_ENMATTER: string;
    PLANET: string;
    ZONE: string;
    CURRENT_SESSION: string;
    FINDER: string;
    FINDERS: string;
    SELECT_FINDER: string;
    FINDER_TT: string;
    NO_FINDERS: string;
    AMPLIFIERS: string;
    NO_AMPLIFIERS: string;
    ENHANCERS: string;
    SOCKET: string;
    NO_ENHANCER: string;
    NO_ENHANCERS: string;
    CLOSE: string;
    SESSIONS_LIST: string;
    ACTIVE_VIEW: string;
    DESCRIPTION: string;
  };
  TRANSACTION_MODAL: {
    CONFIRM: string;
    CHOOSE_INSTANCE: string;
    UNAVAILABLE: string;
    SUBMIT_ERROR: string;
    SELL_DETAILS_NOTICE: string;
    GROSS: string;
    NET: string;
    MARKUP: string;
    FEE: string;
    TOTAL: string;

    QUANTITY: string;
    INSTANCE: string;
    AUTO_COMPUTE: string;
    TYPE_DETAIL: string;
    PURCHASE_QUANTITY: string;
    TYPE_DETAIL_HAND_TO_HAND: string;
    TYPE_DETAIL_FOUND: string;
    TYPE_DETAIL_GIFT: string;
    TYPE_DETAIL_EXISTING_STOCK: string;
    TYPE_DETAIL_GIVEN: string;
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
    REQUIRED: string;
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
