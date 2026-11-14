import { useCallback } from 'react';
import { useQueryContext } from '@/shared/hooks';
import type { TransactionButtonId } from './constants';

export type TransactionAction = 'buy' | 'sell';
export type TransactionContext = {
  type?: TransactionAction;
  item_id?: string;
  lot_id?: string;
  page?: TransactionButtonId;
};
export type TransactionContextUpdate = Partial<{
  [Key in keyof TransactionContext]: TransactionContext[Key] | null;
}>;

/** Return whether a URL value is a valid transaction action. */
function parseTransactionAction(
  value: string | null,
): TransactionAction | undefined {
  return value === 'buy' || value === 'sell' ? value : undefined;
}

/** Return whether a URL value identifies a supported transaction page. */
function parseTransactionPage(
  value: string | null,
): TransactionButtonId | undefined {
  if (!value) return undefined;
  if (
    value === 'finder' ||
    value === 'excavator' ||
    value === 'refiner' ||
    value === 'finder-enhancers' ||
    value === 'finder-excavators' ||
    value === 'materials' ||
    value === 'running-transactions' ||
    value.startsWith('material-type-')
  ) {
    return value as TransactionButtonId;
  }
  return undefined;
}

/** Parse transaction-specific context values from the shared URL context hook. */
export function parseTransactionContext(
  params: URLSearchParams,
): TransactionContext {
  return {
    type: parseTransactionAction(params.get('context_type')),
    item_id: params.get('context_item_id') ?? undefined,
    lot_id: params.get('context_lot_id') ?? undefined,
    page: parseTransactionPage(params.get('context_page')),
  };
}

/** Expose transaction context and its URL-backed update operation. */
export function useTransactionContext() {
  const parse = useCallback(parseTransactionContext, []);
  return useQueryContext<TransactionContext>(parse);
}
