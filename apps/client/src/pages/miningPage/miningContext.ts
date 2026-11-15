import { useCallback } from 'react';

import { useQueryContext } from '@/shared/hooks';

import type { MiningButtonId } from './constants';

export type MiningContext = {
  page?: MiningButtonId;
  session_id?: string;
};

export type MiningContextUpdate = Partial<{
  [Key in keyof MiningContext]: MiningContext[Key] | null;
}>;

/** Return whether a URL value identifies a supported mining page. */
function parseMiningPage(value: string | null): MiningButtonId | undefined {
  if (
    value === 'create-session' ||
    value === 'current-session' ||
    value === 'close' ||
    value === 'sessions-list'
  ) {
    return value;
  }

  return undefined;
}

/** Parse mining navigation values from the shared URL context hook. */
export function parseMiningContext(params: URLSearchParams): MiningContext {
  return {
    page: parseMiningPage(params.get('context_page')),
    session_id: params.get('context_session_id') ?? undefined,
  };
}

/** Expose mining navigation context and its URL-backed update operation. */
export function useMiningContext() {
  const parse = useCallback(parseMiningContext, []);
  return useQueryContext<MiningContext>(parse);
}
