import type { TransactionKind } from '@/shared/types/modal';
import type { ItemRow } from '@/shared/types';

/** Convert a catalogue item kind to the API transaction category. */
export function getTransactionKind(item: ItemRow): TransactionKind {
  if (item.kind === 'material') return 'material';
  if (item.kind.includes('enhancer')) return 'enhancer';
  return 'tool';
}
