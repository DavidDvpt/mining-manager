import { EntropiaImage } from '@/shared/components/entropiaImage';
import { Button } from '@/components/ui/button/button';
import { AppIconName } from '@/shared/components/icon';
import type { ItemStoreColumn, ItemStoreRow } from '@/shared/types/listItem';
import { formatDecimalValue } from '@/shared/utils';
import styles from '../item-store-list.module.scss';

const valueOrDash = (value: unknown) =>
  value === null || value === undefined || value === '' ? '—' : String(value);

/** Create common store columns and optionally include the decay column. */
export const createCommonItemColumns = (
  options: { includeDecay?: boolean } = {},
): ItemStoreColumn[] => {
  const columns: ItemStoreColumn[] = [
    {
      key: 'image',
      label: '',
      flex: '0 0 3.5rem',
      render: (row) => (
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
      label: 'Name',
      flex: '2 1 14rem',
      render: (row) => row.name,
    },
    {
      key: 'tt',
      label: 'TT',
      flex: '0 1 6rem',
      align: 'right',
      render: (row) => formatDecimalValue(row.tt),
    },
  ];

  if (options.includeDecay !== false) {
    columns.push({
      key: 'decay',
      label: 'Decay',
      flex: '0 1 6rem',
      align: 'right',
      render: (row) => formatDecimalValue(row.decay),
    });
  }

  return columns;
};

/** Format a normalized item detail for a compact catalogue cell. */
export const itemDetail = (key: string) => (row: ItemStoreRow) =>
  valueOrDash(row.details[key]);

/** Create the trailing buy action column shared by every item-store list. */
export const createBuyColumn = (
  onBuy?: (row: ItemStoreRow) => void,
): ItemStoreColumn => ({
  key: 'buy',
  label: '',
  kind: 'button',
  flex: '0 0 2.75rem',
  align: 'center',
  render: (row) => (
    <Button
      type="button"
      variant="primary"
      size="small"
      className={styles.buyButton}
      icon={AppIconName.ShoppingCart}
      iconOnly
      aria-label="Buy"
      title="Buy"
      onClick={() => onBuy?.(row)}
    />
  ),
});
/** Create the item financial-summary action column shared by every item-store list. */
export const createSummaryColumn = (): ItemStoreColumn => ({
  key: 'summary',
  label: '',
  kind: 'button',
  flex: '0 0 2.75rem',
  align: 'center',
  render: () => (
    <Button
      type="button"
      variant="ternary"
      size="small"
      icon={AppIconName.ChartNoAxesCombined}
      iconOnly
      aria-label="Financial summary"
      title="Financial summary"
      className={styles.buyButton}
    />
  ),
});
