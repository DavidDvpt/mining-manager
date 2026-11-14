import { EntropiaImage } from '@/shared/components/entropiaImage';
import { AppIconName } from '@/shared/components/icon';
import { createIconColumn } from './createIconColumn';
import type { ItemStoreColumn, ItemStoreRow } from '@/shared/types/listItem';
import { formatDecimalValue } from '@/shared/utils';
import type { TranslationKey } from '@/i18n/types';
import styles from '@/pages/transactionPage/itemStoreList/item-store-list.module.scss';
import appListStyles from '../app-list.module.scss';

const valueOrDash = (value: unknown) =>
  value === null || value === undefined || value === '' ? '—' : String(value);
type Translate = (key: TranslationKey) => string;

/** Create common store columns and optionally include the decay column. */
export const createCommonItemColumns = (
  t: Translate,
  options: { includeDecay?: boolean } = {},
): ItemStoreColumn[] => {
  const columns: ItemStoreColumn[] = [
    {
      key: 'image',
      label: '',
      flex: '0 0 3.5rem',
      cellClassName: appListStyles.imageColumn,
      render: (row) => (
        <EntropiaImage
          url={row.imageUrl}
          alt={row.name}
          size="small"
          className="item-store-image"
        />
      ),
    },
    { key: 'name', label: t('ITEM_STORE.NAME'), flex: '2 1 14rem', render: (row) => row.name },
    {
      key: 'tt',
      label: t('ITEM_STORE.TT'),
      flex: '0 1 6rem',
      align: 'right',
      render: (row) => formatDecimalValue(row.tt),
    },
  ];

  if (options.includeDecay !== false) {
    columns.push({
      key: 'decay',
      label: t('ITEM_STORE.DECAY'),
      flex: '0 1 6rem',
      align: 'right',
      render: (row) => formatDecimalValue(row.decay),
    });
  }

  return columns;
};

/** Create the stock column shared by every catalogue row. */
export const createStockColumn = (t: Translate): ItemStoreColumn => ({
  key: 'stock',
  label: t('ITEM_STORE.STOCK'),
  flex: '0 1 6rem',
  align: 'right',
  render: (row) => row.stock ?? '—',
});

/** Format a normalized item detail for a compact catalogue cell. */
export const itemDetail = (key: string) => (row: ItemStoreRow) =>
  valueOrDash(row.details[key]);

/** Create the trailing buy action column shared by every item-store list. */
export const createBuyColumn = (
  t: Translate,
  onBuy?: (row: ItemStoreRow) => void,
): ItemStoreColumn =>
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
  onSell?: (row: ItemStoreRow) => void,
): ItemStoreColumn =>
  createIconColumn({
    key: 'sell',
    icon: AppIconName.HandCoins,
    variant: 'ternary',
    ariaLabel: t('ITEM_STORE.SELL'),
    title: t('ITEM_STORE.SELL'),
    className: `${styles.buyButton} ${styles.sellButton}`,
    isVisible: (row) => (row.stock ?? 0) > 0,
    onClick: onSell,
  });

/** Create the item financial-summary column shared by every item-store list. */
export const createSummaryColumn = (t: Translate): ItemStoreColumn =>
  createIconColumn({
    key: 'summary',
    icon: AppIconName.ChartNoAxesCombined,
    variant: 'ternary',
    ariaLabel: t('ITEM_STORE.FINANCIAL_SUMMARY'),
    title: t('ITEM_STORE.FINANCIAL_SUMMARY'),
    className: styles.buyButton,
  });

/** Return columns specific to finder catalogue rows. */
export const createFinderColumns = (t: Translate): ItemStoreColumn[] => [
  ...createCommonItemColumns(t),
  { key: 'depth', label: t('ITEM_STORE.DEPTH'), flex: '0 1 7rem', align: 'right', render: itemDetail('depth') },
  { key: 'range', label: t('ITEM_STORE.RANGE'), flex: '0 1 7rem', align: 'right', render: itemDetail('range') },
  { key: 'ammoBurn', label: t('ITEM_STORE.AMMO_BURN'), flex: '0 0 5rem', align: 'right', render: itemDetail('ammo_burn') },
];

/** Return columns specific to excavator catalogue rows. */
export const createExcavatorColumns = (t: Translate): ItemStoreColumn[] => [
  ...createCommonItemColumns(t),
  { key: 'efficiency', label: t('ITEM_STORE.EFFICIENCY'), flex: '0 1 8rem', align: 'right', render: itemDetail('efficiency') },
];

/** Return columns specific to refiner catalogue rows. */
export const createRefinerColumns = (t: Translate): ItemStoreColumn[] => [
  ...createCommonItemColumns(t),
  { key: 'usePerMinute', label: t('ITEM_STORE.USE_PER_MINUTE'), flex: '0 1 7rem', align: 'right', render: itemDetail('use_per_minute') },
];

/** Return columns specific to finder-amplifier catalogue rows. */
export const createFinderAmplifierColumns = (t: Translate): ItemStoreColumn[] => [
  ...createCommonItemColumns(t),
  { key: 'efficiency', label: t('ITEM_STORE.EFFICIENCY'), flex: '0 1 8rem', align: 'right', render: itemDetail('efficiency') },
  { key: 'professionLevel', label: t('ITEM_STORE.LEVEL_MIN'), flex: '0 1 8rem', align: 'right', render: itemDetail('profession_level_min') },
];

/** Return columns specific to enhancer catalogue rows. */
export const createEnhancerColumns = (t: Translate): ItemStoreColumn[] => [
  ...createCommonItemColumns(t, { includeDecay: false }),
  { key: 'type', label: t('ITEM_STORE.TYPE'), flex: '0 1 8rem', render: itemDetail('type') },
  { key: 'bonus', label: t('ITEM_STORE.BONUS'), flex: '0 1 7rem', align: 'right', render: itemDetail('bonus') },
];

/** Return columns specific to material catalogue rows. */
export const createMaterialColumns = (
  t: Translate,
  options: { includeType?: boolean } = {},
): ItemStoreColumn[] => {
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
