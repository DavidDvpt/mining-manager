import type { TranslationKey } from '@/i18n/types';
import type { SidebarButton } from '@/shared/types/layout';
import type { MaterialTypeResponse } from '@/api/generated/model/materialTypeResponse';

type Translate = (key: TranslationKey) => string;

export const FIXED_TRANSACTION_BUTTONS = [
  { id: 'finder', label: 'Finder' },
  { id: 'excavator', label: 'Excavator' },
  { id: 'refiner', label: 'Refiner' },
  { id: 'finder-enhancers', label: 'Finder Enhancers' },
  { id: 'finder-excavators', label: 'Finder Excavators' },
] as const;

export type TransactionButtonId =
  (typeof FIXED_TRANSACTION_BUTTONS)[number]['id']
  | `material-type-${string}`
  | 'materials'
  | 'running-transactions';

/** Build transaction navigation, material choices, and the running-transactions entry. */
export const transactionButtons = (
  t: Translate,
  materialTypes: MaterialTypeResponse[] = [],
): SidebarButton<TransactionButtonId>[] => [
  {
    id: 'running-transactions',
    label: t('TRANSACTIONS.RUNNING_TRANSACTIONS'),
    separatorAfter: true,
    highlighted: true,
  },
  ...FIXED_TRANSACTION_BUTTONS,
  {
    id: 'materials',
    label: t('TRANSACTIONS.MATERIALS'),
    children: materialTypes.map(({ id, name }) => ({
      id: `material-type-${id}`,
      label: name,
    })),
  },
];
