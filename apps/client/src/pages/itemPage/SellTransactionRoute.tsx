import {
  getGetApiV1LotsUnstackableItemItemIdQueryKey,
  getGetApiV1LotsItemIdQueryKey,
  getGetApiV1StorageMaterialStockQueryKey,
  getGetApiV1StorageMaterialMaterialIdStockQueryKey,
  getGetApiV1FindersStockQueryKey,
  getGetApiV1ExcavatorsStockQueryKey,
  getGetApiV1RefinersStockQueryKey,
  getGetApiV1FinderAmplifiersStockQueryKey,
  getGetApiV1TransactionRunningQueryKey,
  useGetApiV1LotsUnstackableItemItemId,
  useGetApiV1LotsItemId,
  usePostApiV1TransactionSellStackable,
  usePostApiV1TransactionSellUnstackable,
} from '@/api/generated/miningManagerAPI';
import { TransactionModal } from '@/shared';
import type { TransactionFormValues } from '@/shared/types/modal';
import { useQueryClient } from '@tanstack/react-query';
import { Navigate, useSearchParams, useNavigate } from 'react-router-dom';
import { useTranslations } from '@/i18n/useTranslations';
import { useTransactionItem } from './useTransactionItem';
import { TransactionRouteStatus } from './TransactionRouteStatus';
import { ItemChoiceModal } from '@/shared/components/modal/itemChoiceModal/ItemChoiceModal';
import { isAvailableTransactionLot } from '@/shared/components/modal/transactionModal/transactionModal.utils';

/** Resolve live stock or the explicitly selected equipment lot and submit the existing sell contract. */
function SellTransactionRoute({
  isChoosing = false,
}: {
  isChoosing?: boolean;
}): import('react').JSX.Element {
  const navigate = useNavigate();
  const { t } = useTranslations();
  const [searchParams] = useSearchParams();
  const { item, isLoading, isError } = useTransactionItem();
  const queryClient = useQueryClient();
  const sellStackable = usePostApiV1TransactionSellStackable();
  const sellUnstackable = usePostApiV1TransactionSellUnstackable();
  const isStackable = Boolean(item?.details.isStackable);
  const requestedLotId = searchParams.get('lotId');
  const itemId = item?.id ?? '';
  const stockQuery = useGetApiV1LotsItemId(itemId, {
    query: {
      queryKey: getGetApiV1LotsItemIdQueryKey(itemId),
      enabled: Boolean(item) && isStackable,
    },
  });
  const lotsQuery = useGetApiV1LotsUnstackableItemItemId(itemId, {
    query: {
      queryKey: getGetApiV1LotsUnstackableItemItemIdQueryKey(itemId),
      enabled: Boolean(item) && !isStackable,
    },
  });
  const selectedLot = lotsQuery.data?.find(
    (lot): boolean =>
      lot.id === requestedLotId && isAvailableTransactionLot(lot, itemId),
  );

  /** Close all workflow steps at the catalogue route, including filtered material views. */
  const close = (): void => navigate(isChoosing ? '../../..' : '../..');

  /** Recheck availability immediately before mutation; the API remains authoritative for concurrent sales. */
  const handleSubmit = async (values: TransactionFormValues): Promise<void> => {
    if (!item) return;
    if (isStackable) {
      const freshStock = await stockQuery.refetch();
      if (freshStock.isError) throw new Error(t('ITEM_STORE.ERROR'));
      if (!freshStock.data || values.quantity > freshStock.data.totalQuantity) {
        throw new Error(t('TRANSACTIONS.QUANTITY_EXCEEDS_STOCK'));
      }
      await sellStackable.mutateAsync({
        data: {
          quantity: values.quantity,
          item_id: item.id,
          tt: values.tt,
          ttc: values.ttc,
        },
      });
    } else {
      const freshLots = await lotsQuery.refetch();
      if (freshLots.isError) throw new Error(t('ITEM_STORE.ERROR'));
      if (
        !freshLots.data?.some(
          (lot): boolean =>
            lot.id === requestedLotId &&
            isAvailableTransactionLot(lot, item.id),
        )
      ) {
        throw new Error(t('TRANSACTION_MODAL.UNAVAILABLE'));
      }
      if (values.tt > (item.tt ?? 0))
        throw new Error(t('TRANSACTIONS.TT_EXCEEDS_BASE'));
      if (!selectedLot) throw new Error(t('TRANSACTION_MODAL.UNAVAILABLE'));
      await sellUnstackable.mutateAsync({
        data: {
          quantity: 1,
          lot_id: selectedLot.id,
          tt: values.tt,
          ttc: values.ttc,
        },
      });
    }
    await Promise.all(
      [
        getGetApiV1LotsUnstackableItemItemIdQueryKey(item.id),
        getGetApiV1LotsItemIdQueryKey(item.id),
        getGetApiV1StorageMaterialStockQueryKey(),
        getGetApiV1StorageMaterialMaterialIdStockQueryKey(item.id),
        getGetApiV1FindersStockQueryKey(),
        getGetApiV1ExcavatorsStockQueryKey(),
        getGetApiV1RefinersStockQueryKey(),
        getGetApiV1FinderAmplifiersStockQueryKey(),
        getGetApiV1TransactionRunningQueryKey(),
      ].map((queryKey): Promise<void> =>
        queryClient.invalidateQueries({ queryKey }),
      ),
    );
    close();
  };

  if (isLoading || isError || !item)
    return <TransactionRouteStatus loading={isLoading} onClose={close} />;
  const inventory = isStackable ? stockQuery : lotsQuery;
  if (inventory.isLoading || inventory.isError)
    return (
      <TransactionRouteStatus loading={inventory.isLoading} onClose={close} />
    );
  if (isStackable) {
    if (isChoosing) return <Navigate to=".." replace />;
    return (
      <TransactionModal
        item={item}
        stock={stockQuery.data?.totalQuantity ?? 0}
        action="sell"
        onSubmit={handleSubmit}
        onClose={close}
      />
    );
  }
  if (isChoosing)
    return (
      <ItemChoiceModal
        item={item}
        lots={lotsQuery.data ?? []}
        onCancel={close}
        onConfirm={(lotId): void =>
          navigate(`..?lotId=${encodeURIComponent(lotId)}`)
        }
      />
    );
  if (!requestedLotId) return <Navigate to="item-choice" replace />;
  if (!selectedLot) return <TransactionRouteStatus onClose={close} />;
  return (
    <TransactionModal
      item={item}
      lot={selectedLot}
      action="sell"
      onSubmit={handleSubmit}
      onClose={close}
    />
  );
}

export default SellTransactionRoute;
