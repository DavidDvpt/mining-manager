import type { TranslationKey } from '@/i18n/types';
import type { SidebarButton } from '@/shared/types/layout';

type Translate = (key: TranslationKey) => string;

export type MiningButtonId =
  | 'create-session'
  | 'current-session'
  | 'close'
  | 'sessions-list';

type MiningNavigationOptions = {
  hasCurrentSession: boolean;
};

/** Build mining navigation and disable actions that do not match session state. */
export const miningButtons = (
  t: Translate,
  { hasCurrentSession }: MiningNavigationOptions,
): SidebarButton<MiningButtonId>[] => [
  {
    id: 'create-session',
    label: t('MINING.CREATE_SESSION'),
    separatorAfter: true,
    highlighted: true,
    disabled: hasCurrentSession,
  },
  {
    id: 'current-session',
    label: t('MINING.CURRENT_SESSION'),
    disabled: !hasCurrentSession,
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
