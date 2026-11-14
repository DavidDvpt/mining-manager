import { useMemo } from 'react';
import { AppList } from '@/shared/appList';
import { useTranslations } from '@/i18n/useTranslations';
import {
  createBuyColumn,
  createEnhancerColumns,
  createExcavatorColumns,
  createFinderAmplifierColumns,
  createFinderColumns,
  createMaterialColumns,
  createRefinerColumns,
  createSellColumn,
  createStockColumn,
  createSummaryColumn,
} from '@/shared/appList/columns';
import type { ItemStoreColumn, ItemStoreListProps } from '@/shared/types/listItem';

/** Render transaction-store catalogue rows with their type-specific columns. */
export function ItemStoreList({
  kind,
  rows,
  isLoading = false,
  isError = false,
  showMaterialType = false,
  onBuy,
  onSell,
}: ItemStoreListProps) {
  const { t } = useTranslations();
  const columns = useMemo<ItemStoreColumn[]>(() => {
    let typeColumns: ItemStoreColumn[] = [];

    switch (kind) {
      case 'finder': typeColumns = createFinderColumns(t); break;
      case 'excavator': typeColumns = createExcavatorColumns(t); break;
      case 'refiner': typeColumns = createRefinerColumns(t); break;
      case 'finder-amplifier': typeColumns = createFinderAmplifierColumns(t); break;
      case 'enhancer': typeColumns = createEnhancerColumns(t); break;
      case 'material':
        typeColumns = createMaterialColumns(t, { includeType: showMaterialType });
        break;
    }

    return [
      ...typeColumns,
      createStockColumn(t),
      createSellColumn(t, onSell),
      createSummaryColumn(t),
      createBuyColumn(t, onBuy),
    ];
  }, [kind, onBuy, onSell, showMaterialType, t]);

  return (
    <AppList
      columns={columns}
      rows={rows}
      isLoading={isLoading}
      isError={isError}
      loadingMessage={t('ITEM_STORE.LOADING')}
      errorMessage={t('ITEM_STORE.ERROR')}
      emptyMessage={t('ITEM_STORE.EMPTY')}
    />
  );
}

export default ItemStoreList;
