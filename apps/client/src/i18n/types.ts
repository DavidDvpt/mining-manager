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
    PROFILE: string;
    LOGOUT: string;
  };
};

type StringKey<T> = Extract<keyof T, string>;

type TranslationPath<T> = {
  [Key in StringKey<T>]: T[Key] extends string
    ? Key
    : `${Key}.${TranslationPath<T[Key]>}`;
}[StringKey<T>];

export type TranslationKey = TranslationPath<TranslationSchema>;
