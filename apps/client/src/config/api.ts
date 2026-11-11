import { env } from './env';

/** Return an API base URL without trailing slashes. */
export function getApiBaseUrl(): string {
  if (import.meta.env.DEV) {
    return '';
  }

  return (env.VITE_API_BASE_URL || '').replace(/\/+$/, '');
}
