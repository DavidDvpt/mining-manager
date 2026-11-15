import type { TranslationKey } from '@/i18n/types';
import type { SidebarButton } from '@/shared/types/layout';

type Translate = (key: TranslationKey) => string;

export type MiningButtonId = 'current-session' | 'close' | 'sessions-list';

/** Build the mining sidebar with the current-session submenu and session list entry. */
export const miningButtons = (t: Translate): SidebarButton<MiningButtonId>[] => [
  {
    id: 'current-session',
    label: t('MINING.CURRENT_SESSION'),
    children: [
      {
        id: 'close',
        label: t('MINING.CLOSE'),
      },
    ],
  },
  {
    id: 'sessions-list',
    label: t('MINING.SESSIONS_LIST'),
  },
];
