import { createCommonItemColumns, itemDetail } from './common';
import type { ItemStoreColumn } from '@/shared/types/listItem';

/** Return columns specific to enhancer catalogue rows. */
export const createEnhancerColumns = (): ItemStoreColumn[] => [
  ...createCommonItemColumns({ includeDecay: false }),
  { key: 'type', label: 'Type', flex: '0 1 8rem', render: itemDetail('type') },
  { key: 'bonus', label: 'Bonus', flex: '0 1 7rem', align: 'right', render: itemDetail('bonus') },
];
