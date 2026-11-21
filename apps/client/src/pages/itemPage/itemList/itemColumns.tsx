import { EntropiaImage } from '@/shared/components/entropiaImage';
import { AppIconName } from '@/shared/components/icon';
import { createIconColumn } from '../../../shared/appList/columns/createIconColumn';
import type { ItemColumn, ItemRow } from '@/shared/types/listItem';
import { formatDecimalValue } from '@/shared/utils';
import { isLimitedItem } from '@/shared/utils';
import type { TranslationKey } from '@/i18n/types';
import styles from './item-list.module.scss';

const valueOrDash = (value: unknown): string =>
  value === null || value === undefined || value === '' ? '—' : String(value);
type Translate = (key: TranslationKey) => string;

/** Create common store columns and optionally include the decay column. */
export const createCommonItemColumns = (
  t: Translate,
  options: { includeDecay?: boolean } = {},
): ItemColumn[] => {
  const columns: ItemColumn[] = [
    {
      key: 'image',
      label: '',
      flex: '0 0 4rem',
      cellClassName: styles.imageColumn,
      render: (row): import('react').JSX.Element => (
        <EntropiaImage
          url={row.imageUrl}
          alt={row.name}
          size="small"
          className="item-store-image"
        />
      ),
    },
    {
      key: 'name',
      label: t('ITEM_STORE.NAME'),
      flex: '1 1 14rem',
      render: (row): string => row.name,
    },
    {
      key: 'tt',
      label: 'TT',
      flex: '0 1 6rem',
      align: 'right',
      render: (row): string => formatDecimalValue(row.tt),
    },
  ];

  if (options.includeDecay !== false) {
    columns.push({
      key: 'decay',
      label: t('ITEM_STORE.DECAY'),
      flex: '0 1 6rem',
      align: 'right',
      render: (row): string => formatDecimalValue(row.decay),
    });
  }

  return columns;
};

/** Create the stock column shared by every catalogue row. */
export const createStockColumn = (t: Translate): ItemColumn => ({
  key: 'stock',
  label: t('ITEM_STORE.STOCK'),
  flex: '0 1 6rem',
  align: 'right',
  render: (row): number | '—' => row.stock ?? '—',
});

/** Format a normalized item detail for a compact catalogue cell. */
export const itemDetail =
  (key: string): ((row: ItemRow) => string) =>
  (row: ItemRow): string =>
    valueOrDash(row.details[key]);

/** Create the trailing buy action column shared by every item-store list. */
export const createBuyColumn = (
  t: Translate,
  onBuy?: (row: ItemRow) => void,
): ItemColumn =>
  createIconColumn({
    key: 'buy',
    icon: AppIconName.ShoppingCart,
    variant: 'primary',
    ariaLabel: t('ITEM_STORE.BUY'),
    title: t('ITEM_STORE.BUY'),
    className: styles.buyButton,
    onClick: onBuy,
  });

/** Create the sell action column, hiding the action when stock is empty. */
export const createSellColumn = (
  t: Translate,
  onSell?: (row: ItemRow) => void,
): ItemColumn =>
  createIconColumn({
    key: 'sell',
    icon: AppIconName.HandCoins,
    variant: 'ternary',
    ariaLabel: t('ITEM_STORE.SELL'),
    title: t('ITEM_STORE.SELL'),
    className: `${styles.buyButton} ${styles.sellButton}`,
    isVisible: (row): boolean => (row.stock ?? 0) > 0,
    onClick: onSell,
  });

/** Create the primary edit action for owned editable tool rows. */
export const createEditColumn = (
  t: Translate,
  onEdit?: (row: ItemRow) => void,
): ItemColumn =>
  createIconColumn({
    key: 'edit',
    icon: AppIconName.Pencil,
    variant: 'primary',
    ariaLabel: t('ITEM_STORE.EDIT'),
    title: t('ITEM_STORE.EDIT'),
    className: styles.buyButton,
    isVisible: (row): boolean => {
      const isEditableTool =
        row.kind === 'finder' ||
        row.kind === 'excavator' ||
        (!isLimitedItem(row) &&
          (row.kind === 'refiner' || row.kind === 'finder-amplifier'));
      return isEditableTool && (row.stock ?? 0) > 0;
    },
    onClick: onEdit,
  });

/** Create the item financial-summary column shared by every item-store list. */
export const createSummaryColumn = (t: Translate): ItemColumn =>
  createIconColumn({
    key: 'summary',
    icon: AppIconName.ChartNoAxesCombined,
    variant: 'ternary',
    ariaLabel: t('ITEM_STORE.FINANCIAL_SUMMARY'),
    title: t('ITEM_STORE.FINANCIAL_SUMMARY'),
    className: styles.buyButton,
  });

/** Return columns specific to finder catalogue rows. */
export const createFinderColumns = (t: Translate): ItemColumn[] => [
  ...createCommonItemColumns(t),
  {
    key: 'depth',
    label: t('ITEM_STORE.DEPTH'),
    flex: '0 1 7rem',
    align: 'right',
    render: itemDetail('depth'),
  },
  {
    key: 'range',
    label: t('ITEM_STORE.RANGE'),
    flex: '0 1 7rem',
    align: 'right',
    render: itemDetail('range'),
  },
  {
    key: 'ammoBurn',
    label: t('ITEM_STORE.AMMO_BURN'),
    flex: '0 0 5rem',
    align: 'right',
    render: itemDetail('ammoBurn'),
  },
];

/** Return columns specific to excavator catalogue rows. */
export const createExcavatorColumns = (t: Translate): ItemColumn[] => [
  ...createCommonItemColumns(t),
  {
    key: 'efficiency',
    label: t('ITEM_STORE.EFFICIENCY'),
    flex: '0 1 8rem',
    align: 'right',
    render: itemDetail('efficiency'),
  },
];

/** Return columns specific to refiner catalogue rows. */
export const createRefinerColumns = (t: Translate): ItemColumn[] => [
  ...createCommonItemColumns(t),
  {
    key: 'usePerMinute',
    label: t('ITEM_STORE.USE_PER_MINUTE'),
    flex: '0 1 7rem',
    align: 'right',
    render: itemDetail('usePerMinute'),
  },
];

/** Return columns specific to finder-amplifier catalogue rows. */
export const createFinderAmplifierColumns = (t: Translate): ItemColumn[] => [
  ...createCommonItemColumns(t),
  {
    key: 'efficiency',
    label: t('ITEM_STORE.EFFICIENCY'),
    flex: '0 1 8rem',
    align: 'right',
    render: itemDetail('efficiency'),
  },
  {
    key: 'professionLevel',
    label: t('ITEM_STORE.LEVEL_MIN'),
    flex: '0 1 8rem',
    align: 'right',
    render: itemDetail('professionLevelMin'),
  },
];

/** Return columns specific to enhancer catalogue rows. */
export const createEnhancerColumns = (t: Translate): ItemColumn[] => [
  ...createCommonItemColumns(t, { includeDecay: false }),
  {
    key: 'type',
    label: t('ITEM_STORE.TYPE'),
    flex: '0 1 8rem',
    render: itemDetail('type'),
  },
  {
    key: 'bonus',
    label: t('ITEM_STORE.BONUS'),
    flex: '0 1 7rem',
    align: 'right',
    render: itemDetail('bonus'),
  },
];

/** Return columns specific to material catalogue rows. */
export const createMaterialColumns = (
  t: Translate,
  options: { includeType?: boolean } = {},
): ItemColumn[] => {
  const columns = createCommonItemColumns(t, { includeDecay: false });

  if (options.includeType) {
    columns.splice(2, 0, {
      key: 'type',
      label: t('ITEM_STORE.TYPE'),
      flex: '0 1 10rem',
      render: itemDetail('type'),
    });
  }

  return columns;
};
