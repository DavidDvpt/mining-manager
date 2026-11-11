import type { AxiosRequestConfig } from 'axios';

export type ApiErrorBody = {
  message?: string;
  errors?: ValidationError[];
};

export type ValidationError = {
  path: string;
  code: string;
  message: string;
};

export type ApiErrorKind = 'http' | 'network' | 'timeout' | 'unknown';

/** Stable error exposed to frontend consumers instead of raw Axios failures. */
export class ApiError extends Error {
  readonly status: number;
  readonly kind: ApiErrorKind;
  readonly code?: string;
  readonly validationErrors?: ValidationError[];

  /** Create an API error with transport, HTTP, and validation context. */
  constructor({
    status,
    kind,
    message,
    code,
    validationErrors,
  }: {
    status: number;
    kind: ApiErrorKind;
    message: string;
    code?: string;
    validationErrors?: ValidationError[];
  }) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.kind = kind;
    this.code = code;
    this.validationErrors = validationErrors;
  }
}

export type ApiErrorShape = {
  status: number;
  message: string;
  kind: ApiErrorKind;
  code?: string;
  validationErrors?: ValidationError[];
};

export type AuthenticatedRequestConfig = AxiosRequestConfig & {
  authRetry?: boolean;
};
