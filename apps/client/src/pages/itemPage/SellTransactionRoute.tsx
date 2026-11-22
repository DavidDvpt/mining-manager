import {
  getGetApiV1LotsUnstackableItemItemIdQueryKey,
  useGetApiV1LotsUnstackableItemItemId,
  getGetApiV1StorageMaterialMaterialIdStockQueryKey,
  getGetApiV1StorageMaterialStockQueryKey,
  usePostApiV1TransactionSellStackable,
  usePostApiV1TransactionSellUnstackable,
} from '@/api/generated/miningManagerAPI';
import { TransactionModal, TransactionForm } from '@/shared';
import type { ItemRow } from '@/shared';
import type {
  TransactionFormValues,
  TransactionItem,
  TransactionLot,
} from '@/shared/types/modal';
import { JSX, useMemo, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useSearchParams, useNavigate } from 'react-router-dom';

/** Parse the catalogue item and prepare owned lots before opening the sell modal. */
function SellTransactionRoute(): JSX.Element | null {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const serializedItem = searchParams.get('item');
  const item: ItemRow | null = useMemo(
    () => (serializedItem ? JSON.parse(serializedItem) : null),
    [serializedItem],
  );
  const queryClient = useQueryClient();
  const sellStackable = usePostApiV1TransactionSellStackable();
  const sellUnstackable = usePostApiV1TransactionSellUnstackable();
  const [validationError, setValidationError] = useState<string | null>(null);
  const isStackable = Boolean(item?.details.isStackable);
  const requestedLotId = searchParams.get('lotId');
  const lotsQuery = useGetApiV1LotsUnstackableItemItemId(item?.id ?? '', {
    query: {
      queryKey: getGetApiV1LotsUnstackableItemItemIdQueryKey(item?.id ?? ''),
      enabled: item !== null && !isStackable,
    },
  });
  const selectedLot: TransactionLot | null = requestedLotId
    ? (lotsQuery.data?.find(({ id }): boolean => id === requestedLotId) ?? null)
    : (lotsQuery.data?.[0] ?? null);
  const transactionItem: TransactionItem | null = useMemo(
    () =>
      !item
        ? null
        : isStackable
          ? item
          : selectedLot
            ? {
                ...item,
                name: `${item.name} T${selectedLot.tier ?? 0}`,
                ttRemaining: selectedLot.ttRemaining ?? selectedLot.tt,
              }
            : null,
    [item, isStackable, selectedLot],
  );

  /** Validate the requested quantity or TT, submit the sale, and refresh stock. */
  const handleSubmit = async (values: TransactionFormValues): Promise<void> => {
    if (!item) return;
    if (isStackable && values.quantity > (item.stock ?? 0)) {
      setValidationError(
        'La quantité ne peut pas dépasser le stock disponible.',
      );
      return;
    }
    if (!isStackable && values.tt > (item.tt ?? 0)) {
      setValidationError(
        'Le TT ne peut pas dépasser la valeur TT de base de l’objet.',
      );
      return;
    }
    setValidationError(null);
    if (isStackable) {
      await sellStackable.mutateAsync({
        data: {
          quantity: values.quantity,
          item_id: item.id,
          tt: values.tt,
          ttc: values.ttc,
        },
      });
      if (item.kind === 'material') {
        const stockKey = getGetApiV1StorageMaterialStockQueryKey();
        queryClient.setQueryData<Record<string, number>>(
          stockKey,
          (stock = {}) => ({
            ...stock,
            [item.id]: Math.max(
              0,
              (stock[item.id] ?? item.stock ?? 0) - values.quantity,
            ),
          }),
        );
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: stockKey }),
          queryClient.invalidateQueries({
            queryKey: getGetApiV1StorageMaterialMaterialIdStockQueryKey(
              item.id,
            ),
          }),
        ]);
      }
    } else {
      if (!selectedLot) return;
      await sellUnstackable.mutateAsync({
        data: {
          quantity: 1,
          lot_id: selectedLot.id,
          tt: values.tt,
          ttc: values.ttc,
        },
      });
      await queryClient.invalidateQueries({
        queryKey: getGetApiV1LotsUnstackableItemItemIdQueryKey(item.id),
      });
    }
    navigate('../..');
  };

  return (
    <TransactionModal
      item={transactionItem}
      action="sell"
      onSubmit={handleSubmit}
      onClose={(): void => navigate('../..')}
      validationError={validationError}
    >
      <TransactionForm
        action="sell"
        isStackable={isStackable}
        item={transactionItem}
      />
    </TransactionModal>
  );
}

export default SellTransactionRoute;
