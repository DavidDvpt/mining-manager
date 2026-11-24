import type { TransactionKind, TransactionLot } from '@/shared/types/modal';
import type { ItemRow } from '@/shared/types';

/** Convert a catalogue item kind to the API transaction category. */
export function getTransactionKind(item: ItemRow): TransactionKind {
  if (item.kind === 'material') return 'material';
  if (item.kind.includes('enhancer')) return 'enhancer';
  return 'tool';
}

/** Accept only active, unreserved single-instance lots belonging to the URL item. */
export function isAvailableTransactionLot(
  lot: TransactionLot,
  itemId: string,
): boolean {
  return (
    lot.item.id === itemId &&
    lot.isActive &&
    lot.qty === 1 &&
    lot.reserved === 0
  );
}
