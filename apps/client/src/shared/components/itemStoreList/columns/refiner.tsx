import { createCommonItemColumns, itemDetail } from './common';
import type { ItemStoreColumn } from '@/shared/types/listItem';

/** Return columns specific to refiner catalogue rows. */
export const createRefinerColumns = (): ItemStoreColumn[] => [
  ...createCommonItemColumns(),
  { key: 'usePerMinute', label: 'Use / min', flex: '0 1 7rem', align: 'right', render: itemDetail('use_per_minute') },
];
