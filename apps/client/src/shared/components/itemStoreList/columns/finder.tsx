import { createCommonItemColumns, itemDetail } from './common';
import type { ItemStoreColumn } from '@/shared/types/listItem';

/** Return columns specific to finder catalogue rows. */
export const createFinderColumns = (): ItemStoreColumn[] => [
  ...createCommonItemColumns(),
  { key: 'depth', label: 'Depth', flex: '0 1 7rem', align: 'right', render: itemDetail('depth') },
  { key: 'range', label: 'Range', flex: '0 1 7rem', align: 'right', render: itemDetail('range') },
];
