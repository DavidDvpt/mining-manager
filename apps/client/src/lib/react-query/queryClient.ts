import { QueryClient } from '@tanstack/react-query';
import { ApiError } from '@/lib/axios/types';

/** Retry transient query failures, but never repeat an authentication failure. */
function shouldRetryQuery(failureCount: number, error: unknown): boolean {
  if (failureCount >= 1) {
    return false;
  }

  if (error instanceof ApiError) {
    return error.status === 0 || error.status >= 500;
  }

  return true;
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      gcTime: 5 * 60_000,
      refetchOnWindowFocus: false,
      retry: shouldRetryQuery,
    },
    mutations: {
      retry: 0,
    },
  },
});

export { queryClient };
