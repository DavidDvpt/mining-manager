import { createCommonItemColumns, itemDetail } from './common';
import type { ItemStoreColumn } from '@/shared/types/listItem';

/** Return columns specific to material catalogue rows. */
export const createMaterialColumns = (
  options: { includeType?: boolean } = {},
): ItemStoreColumn[] => {
  const columns = createCommonItemColumns({ includeDecay: false });

  if (options.includeType) {
    columns.splice(2, 0, {
      key: 'type',
      label: 'Type',
      flex: '0 1 10rem',
      render: itemDetail('type'),
    });
  }

  return columns;
};
