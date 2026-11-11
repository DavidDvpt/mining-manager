import type { AxiosRequestConfig } from 'axios';
import {
  axiosPrivateInstance,
  axiosPublicInstance,
} from '../../lib/axios/instances';
import type { ApiError } from '../../lib/axios/types';

type OrvalRequestConfig = AxiosRequestConfig & {
  data?: unknown;
};

const publicRoutes = new Set([
  '/signin',
  '/signup',
  '/refresh-token',
  '/logout',
]);

/** Return whether an Orval request is allowed without private retry handling. */
function isPublicRoute(url?: string): boolean {
  const path = url?.split('?', 1)[0];
  return path !== undefined && publicRoutes.has(path);
}

/** Execute generated requests through the cookie-authenticated Axios layer. */
export const customInstance = <T>(
  config: OrvalRequestConfig,
  options?: OrvalRequestConfig,
): Promise<T> => {
  const requestConfig = { ...config, ...options };
  const client = isPublicRoute(requestConfig.url)
    ? axiosPublicInstance
    : axiosPrivateInstance;

  return client.request<T>(requestConfig).then(({ data }) => data);
};

export type ErrorType<_Error> = ApiError;
export type BodyType<BodyData> = BodyData;

export default customInstance;
