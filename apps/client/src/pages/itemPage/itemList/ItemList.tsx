import { JSX, useMemo } from 'react';
import { AppList } from '@/shared/appList';
import { useTranslations } from '@/i18n/useTranslations';
import {
  createBuyColumn,
  createEnhancerColumns,
  createEditColumn,
  createExcavatorColumns,
  createFinderAmplifierColumns,
  createFinderColumns,
  createMaterialColumns,
  createRefinerColumns,
  createSellColumn,
  createStockColumn,
  createSummaryColumn,
} from './itemColumns';
import type { ItemColumn, ItemListProps } from '@/shared/types/listItem';

export function ItemList({
  kind,
  rows,
  isLoading = false,
  isError = false,
  showMaterialType = false,
  onBuy,
  onSell,
  onEdit,
}: ItemListProps): JSX.Element {
  const { t } = useTranslations();
  const columns = useMemo<ItemColumn[]>((): ItemColumn[] => {
    let typeColumns: ItemColumn[] = [];

    switch (kind) {
      case 'finder':
        typeColumns = createFinderColumns(t);
        break;
      case 'excavator':
        typeColumns = createExcavatorColumns(t);
        break;
      case 'refiner':
        typeColumns = createRefinerColumns(t);
        break;
      case 'finder-amplifier':
        typeColumns = createFinderAmplifierColumns(t);
        break;
      case 'finder-enhancer':
      case 'excavator-enhancer':
        typeColumns = createEnhancerColumns(t);
        break;
      case 'material':
        typeColumns = createMaterialColumns(t, {
          includeType: showMaterialType,
        });
        break;
    }

    const editColumn = createEditColumn(t, onEdit);
    const nameColumnIndex = typeColumns.findIndex(
      (column): boolean => column.key === 'name',
    );
    const columnsWithEdit =
      nameColumnIndex === -1
        ? [...typeColumns, editColumn]
        : [
            ...typeColumns.slice(0, nameColumnIndex + 1),
            editColumn,
            ...typeColumns.slice(nameColumnIndex + 1),
          ];

    return [
      ...columnsWithEdit,
      createStockColumn(t),
      createSellColumn(t, onSell),
      createSummaryColumn(t),
      createBuyColumn(t, onBuy),
    ];
  }, [kind, onBuy, onEdit, onSell, showMaterialType, t]);

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

export default ItemList;
