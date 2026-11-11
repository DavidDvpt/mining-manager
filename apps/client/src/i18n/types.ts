export type TranslationSchema = {
  AUTH: {
    SIGNIN: {
      TITLE: string;
      SUBTITLE: string;
      PSEUDO: string;
      PASSWORD: string;
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
  };
};

type StringKey<T> = Extract<keyof T, string>;

type TranslationPath<T> = {
  [Key in StringKey<T>]: T[Key] extends string
    ? Key
    : `${Key}.${TranslationPath<T[Key]>}`;
}[StringKey<T>];

export type TranslationKey = TranslationPath<TranslationSchema>;
