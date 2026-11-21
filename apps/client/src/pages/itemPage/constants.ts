import type { TranslationKey } from '@/i18n/types';
import type { MaterialTypeResponse } from '@/api/generated/model/materialTypeResponse';
import { toSlug } from '@/shared/utils/string';
import type { SidebarButtonType } from '@/shared';
import { TransactionButtonId } from '@/pages/itemPage/itemPageType';

type Translate = (key: TranslationKey) => string;

export const FIXED_SIDEBAR_ITEM_BUTTONS = [
  { id: 'finder', label: 'Finder', linkTo: '/items/finders' },
  { id: 'excavator', label: 'Excavator', linkTo: '/items/excavators' },
  { id: 'refiner', label: 'Refiner', linkTo: '/items/refiners' },
  {
    id: 'finder-enhancers',
    label: 'Finder Enhancers',
    linkTo: '/items/finder-enhancers',
  },
  {
    id: 'excavator-enhancers',
    label: 'Excavator Enhancers',
    linkTo: '/items/excavator-enhancers',
  },
] as const;

/** Build transaction navigation, material choices, and the running-transactions entry. */
export const transactionButtons = (
  t: Translate,
  materialTypes: MaterialTypeResponse[] = [],
): SidebarButtonType<TransactionButtonId>[] => {
  return [
    {
      id: 'running-transactions',
      label: t('TRANSACTIONS.RUNNING_TRANSACTIONS'),
      linkTo: '/items/running-transactions',
      separatorAfter: true,
      highlighted: true,
    },
    ...FIXED_SIDEBAR_ITEM_BUTTONS,
    {
      id: 'materials',
      label: t('TRANSACTIONS.MATERIALS'),
      linkTo: '/items/materials',
      children: materialTypes.map(
        ({
          id,
          name,
        }): { id: `material-${string}`; label: string; linkTo: string } => ({
          id: `material-${id}`,
          label: name,
          linkTo: `materials/${toSlug(name)}`,
        }),
      ),
    },
  ];
};
