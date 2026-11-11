import { createCommonItemColumns, itemDetail } from './common';
import type { ItemStoreColumn } from '@/shared/types/listItem';

/** Return columns specific to material catalogue rows. */
export const createMaterialColumns = (): ItemStoreColumn[] => [
  ...createCommonItemColumns({ includeDecay: false }),
  { key: 'type', label: 'Type', flex: '0 1 10rem', render: itemDetail('type') },
];
