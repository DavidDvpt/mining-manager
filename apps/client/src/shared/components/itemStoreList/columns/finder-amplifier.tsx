import { createCommonItemColumns, itemDetail } from './common';
import type { ItemStoreColumn } from '@/shared/types/listItem';

/** Return columns specific to finder-amplifier catalogue rows. */
export const createFinderAmplifierColumns = (): ItemStoreColumn[] => [
  ...createCommonItemColumns(),
  { key: 'efficiency', label: 'Efficiency', flex: '0 1 8rem', align: 'right', render: itemDetail('efficiency') },
  { key: 'professionLevel', label: 'Level min.', flex: '0 1 8rem', align: 'right', render: itemDetail('profession_level_min') },
];
