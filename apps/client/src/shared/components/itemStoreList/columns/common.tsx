import { EntropiaImage } from '@/shared/components/entropiaImage';
import type { ItemStoreColumn, ItemStoreRow } from '@/shared/types/listItem';

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
      render: (row) => valueOrDash(row.tt),
    },
  ];

  if (options.includeDecay !== false) {
    columns.push({
      key: 'decay',
      label: 'Decay',
      flex: '0 1 6rem',
      align: 'right',
      render: (row) => valueOrDash(row.decay),
    });
  }

  return columns;
};

/** Format a normalized item detail for a compact catalogue cell. */
export const itemDetail = (key: string) => (row: ItemStoreRow) =>
  valueOrDash(row.details[key]);
