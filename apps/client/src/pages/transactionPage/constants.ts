import type { TranslationKey } from '@/i18n/types';
import type { SidebarButton } from '@/shared/types/layout';

type Translate = (key: TranslationKey) => string;

/** Build the translated sidebar actions for the transactions page. */
export const transactionButtons = (t: Translate): SidebarButton[] => [
  { id: 'owned', label: t('TRANSACTIONS.OWNED') },
  { id: 'tools', label: t('TRANSACTIONS.TOOLS') },
  { id: 'accessories', label: t('TRANSACTIONS.ACCESSORIES') },
  {
    id: 'materials',
    label: t('TRANSACTIONS.MATERIALS'),
    children: [
      { id: 'materials-ores', label: t('TRANSACTIONS.ORES') },
      { id: 'materials-enmat', label: t('TRANSACTIONS.ENMAT') },
      { id: 'materials-refined', label: t('TRANSACTIONS.REFINED') },
    ],
  },
];
