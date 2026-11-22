import { useQueryClient } from '@tanstack/react-query';
import {
  getGetApiV1ExcavatorsStockQueryKey,
  getGetApiV1FinderAmplifiersStockQueryKey,
  getGetApiV1FindersStockQueryKey,
  getGetApiV1RefinersStockQueryKey,
  getGetApiV1StorageMaterialMaterialIdStockQueryKey,
  getGetApiV1StorageMaterialStockQueryKey,
  usePostApiV1TransactionBuyStackable,
  usePostApiV1TransactionBuyUnstackable,
} from '@/api/generated/miningManagerAPI';
import type { TransactionFormValues } from '@/shared/types/modal';
import { TransactionForm, TransactionModal } from '@/shared';
import { getTransactionKind } from '@/shared/components/modal/transactionModal/transactionModal.utils';
import type { ItemRow } from '@/shared/types';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useMemo } from 'react';

/** Prepare the selected item and submit purchases through the shared modal. */
function BuyTransactionRoute(): import('react').JSX.Element | null {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const serializedItem = searchParams.get('item');
  const item: ItemRow | null = useMemo(
    () => (serializedItem ? JSON.parse(serializedItem) : null),
    [serializedItem],
  );
  const queryClient = useQueryClient();
  const buyStackable = usePostApiV1TransactionBuyStackable();
  const buyUnstackable = usePostApiV1TransactionBuyUnstackable();
  const isStackable = Boolean(item?.details.isStackable);

  /** Validate and persist the buy request matching the item's stackability. */
  const handleSubmit = async (
    formValues: TransactionFormValues,
  ): Promise<void> => {
    if (!item) return;
    let queryKeys = [];
    const kind = getTransactionKind(item);

    if (isStackable && item.stock === null) {
      throw new Error('Stackable buy requires item stock.');
    }
    if (isStackable) {
      await buyStackable.mutateAsync({
        data: {
          quantity: formValues.quantity,
          kind,
          type_detail: formValues.type_detail,
          item_id: item.id,
          fee: formValues.fee,
          ttc: formValues.ttc,
        },
      });
      queryKeys = [
        getGetApiV1StorageMaterialStockQueryKey(),
        getGetApiV1StorageMaterialMaterialIdStockQueryKey(item.id),
      ];
    } else {
      await buyUnstackable.mutateAsync({
        data: {
          quantity: 1,
          purchase_quantity: formValues.purchase_quantity,
          kind,
          type_detail: formValues.type_detail,
          item_id: item.id,
          tt: formValues.tt,
          fee: formValues.fee,
          ttc: formValues.ttc,
        },
      });
      queryKeys = [
        getGetApiV1FindersStockQueryKey(),
        getGetApiV1ExcavatorsStockQueryKey(),
        getGetApiV1RefinersStockQueryKey(),
        getGetApiV1FinderAmplifiersStockQueryKey(),
      ];
    }
    await Promise.all(
      queryKeys.map((queryKey): Promise<void> =>
        queryClient.invalidateQueries({ queryKey }),
      ),
    );
    navigate('../..');
  };

  if (!item) return null;
  return (
    <TransactionModal
      item={item}
      action="buy"
      onSubmit={handleSubmit}
      onClose={(): void => navigate('../..')}
    >
      <TransactionForm action="buy" isStackable={isStackable} item={item} />
    </TransactionModal>
  );
}

export default BuyTransactionRoute;
