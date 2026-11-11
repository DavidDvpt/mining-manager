import type {
  AxiosError,
  AxiosInstance,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios';
import {
  ApiError,
  type ApiErrorBody,
  type AuthenticatedRequestConfig,
  type ValidationError,
} from './types';

let refreshPromise: Promise<void> | null = null;

/** Return whether a request is one of the authentication endpoints. */
function isAuthenticationRequest(url: string): boolean {
  return ['/signin', '/signup', '/refresh-token', '/logout'].some((path) =>
    url.includes(path),
  );
}

/** Convert an Axios failure into the frontend API error contract. */
export function normalizeApiError(error: AxiosError<ApiErrorBody>): ApiError {
  if (error instanceof ApiError) {
    return error;
  }

  if (!error.response) {
    const isTimeout = error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT';
    return new ApiError({
      status: 0,
      kind: isTimeout ? 'timeout' : 'network',
      code: error.code,
      message: isTimeout
        ? 'The request timed out.'
        : 'The API could not be reached.',
    });
  }

  const { status, data } = error.response;
  const validationErrors = Array.isArray(data?.errors)
    ? data.errors.filter(isValidationError)
    : undefined;

  return new ApiError({
    status,
    kind: 'http',
    code: error.code,
    message: data?.message ?? fallbackMessage(status),
    validationErrors: validationErrors?.length ? validationErrors : undefined,
  });
}

/** Return a stable fallback message for an HTTP status without a response message. */
function fallbackMessage(status: number): string {
  const messages: Record<number, string> = {
    401: 'Authentication required.',
    403: 'You are not allowed to perform this action.',
    404: 'The requested resource was not found.',
    409: 'The request conflicts with existing data.',
    422: 'The submitted data is invalid.',
    500: 'The server encountered an unexpected error.',
  };

  return messages[status] ?? 'The API returned an error.';
}

/** Validate the API shape before exposing a field-level validation error. */
function isValidationError(value: unknown): value is ValidationError {
  if (!value || typeof value !== 'object') {
    return false;
  }

  const candidate = value as Partial<ValidationError>;
  return (
    typeof candidate.path === 'string' &&
    typeof candidate.code === 'string' &&
    typeof candidate.message === 'string'
  );
}

/** Refresh the HttpOnly authentication cookies once for concurrent requests. */
async function refreshAuthentication(
  publicClient: AxiosInstance,
): Promise<void> {
  if (!refreshPromise) {
    refreshPromise = publicClient
      .post('/refresh-token')
      .then(() => undefined)
      .finally(() => {
        refreshPromise = null;
      });
  }

  await refreshPromise;
}

/** Attach a no-op request interceptor while keeping credentials cookie-only. */
export function attachPrivateRequestInterceptor(instance: AxiosInstance): void {
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => config,
    (error) => Promise.reject(error),
  );
}

/** Attach one guarded cookie refresh and retry for expired authenticated calls. */
export function attachPrivateResponseInterceptor(
  privateClient: AxiosInstance,
  publicClient: AxiosInstance,
): void {
  privateClient.interceptors.response.use(
    (response: AxiosResponse) => response,
    async (error: AxiosError<ApiErrorBody>) => {
      const config = error.config as AuthenticatedRequestConfig | undefined;
      const requestUrl = config?.url ?? '';
      const shouldRefresh =
        error.response?.status === 401 &&
        Boolean(config) &&
        !config?.authRetry &&
        !isAuthenticationRequest(requestUrl);

      if (shouldRefresh && config) {
        try {
          await refreshAuthentication(publicClient);
          config.authRetry = true;
          return privateClient(config);
        } catch {
          // Fall through to the normalized error returned below.
        }
      }

      return Promise.reject(normalizeApiError(error));
    },
  );
}
