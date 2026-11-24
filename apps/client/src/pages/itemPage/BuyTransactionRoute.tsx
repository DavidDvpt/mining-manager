import { useQueryClient, type QueryKey } from '@tanstack/react-query';
import {
  getGetApiV1LotsItemIdQueryKey,
  getGetApiV1LotsUnstackableItemItemIdQueryKey,
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
import { TransactionModal } from '@/shared';
import { getTransactionKind } from '@/shared/components/modal/transactionModal/transactionModal.utils';
import { useNavigate } from 'react-router-dom';
import { useTransactionItem } from './useTransactionItem';
import { TransactionRouteStatus } from './TransactionRouteStatus';

/** Prepare the selected item and submit purchases through the shared modal. */
function BuyTransactionRoute(): import('react').JSX.Element | null {
  const navigate = useNavigate();
  const { item, isLoading, isError } = useTransactionItem();
  const queryClient = useQueryClient();
  const buyStackable = usePostApiV1TransactionBuyStackable();
  const buyUnstackable = usePostApiV1TransactionBuyUnstackable();
  const isStackable = Boolean(item?.details.isStackable);

  /** Validate and persist the buy request matching the item's stackability. */
  const handleSubmit = async (
    formValues: TransactionFormValues,
  ): Promise<void> => {
    if (!item) return;
    let queryKeys: QueryKey[] = [];
    const kind = getTransactionKind(item);

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
    queryKeys.push(
      getGetApiV1LotsItemIdQueryKey(item.id),
      getGetApiV1LotsUnstackableItemItemIdQueryKey(item.id),
    );
    await Promise.all(
      queryKeys.map((queryKey): Promise<void> =>
        queryClient.invalidateQueries({ queryKey }),
      ),
    );
    navigate('../..');
  };

  if (isLoading || isError || !item)
    return (
      <TransactionRouteStatus
        loading={isLoading}
        onClose={(): void => navigate('../..')}
      />
    );
  return (
    <TransactionModal
      item={item}
      action="buy"
      onSubmit={handleSubmit}
      onClose={(): void => navigate('../..')}
    />
  );
}

export default BuyTransactionRoute;
