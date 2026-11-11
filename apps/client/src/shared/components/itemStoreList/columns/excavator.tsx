import { createCommonItemColumns, itemDetail } from './common';
import type { ItemStoreColumn } from '@/shared/types/listItem';

/** Return columns specific to excavator catalogue rows. */
export const createExcavatorColumns = (): ItemStoreColumn[] => [
  ...createCommonItemColumns(),
  { key: 'efficiency', label: 'Efficiency', flex: '0 1 8rem', align: 'right', render: itemDetail('efficiency') },
];
