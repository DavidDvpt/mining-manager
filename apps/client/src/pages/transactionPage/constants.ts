import type { TranslationKey } from '@/i18n/types';
import type { SidebarButton } from '@/shared/types/layout';
import type { MaterialTypeResponse } from '@/api/generated/model/materialTypeResponse';

type Translate = (key: TranslationKey) => string;

/** Build transaction navigation and append material types returned by the API. */
export const transactionButtons = (
  t: Translate,
  materialTypes: MaterialTypeResponse[] = [],
): SidebarButton[] => [
  { id: 'owned', label: t('TRANSACTIONS.OWNED') },
  { id: 'tools', label: t('TRANSACTIONS.TOOLS') },
  { id: 'accessories', label: t('TRANSACTIONS.ACCESSORIES') },
  {
    id: 'materials',
    label: t('TRANSACTIONS.MATERIALS'),
    children: materialTypes.map(({ id, name }) => ({
      id: `material-type-${id}`,
      label: name,
    })),
  },
];
