import type { TranslationKey } from '@/i18n/types';
import type { SidebarButtonType } from '@/shared/types/layout';

type Translate = (key: TranslationKey) => string;

export type MiningButtonId =
  'create-session' | 'current-session' | 'close' | 'sessions-list';

type MiningNavigationOptions = {
  hasCurrentSession: boolean;
  currentSessionId?: string;
};

/** Build mining navigation and disable actions that do not match session state. */
export const miningButtons = (
  t: Translate,
  { hasCurrentSession, currentSessionId }: MiningNavigationOptions,
): SidebarButtonType<MiningButtonId>[] => [
  {
    id: 'create-session',
    linkTo: '/mining/create',
    label: t('MINING.CREATE_SESSION'),
    separatorAfter: true,
    highlighted: true,
    disabled: hasCurrentSession,
  },
  {
    id: 'current-session',
    linkTo: currentSessionId
      ? `/mining/${currentSessionId}/running`
      : '/mining/current',
    label: t('MINING.CURRENT_SESSION'),
    disabled: !hasCurrentSession,
    children: [
      {
        id: 'close',
        linkTo: currentSessionId
          ? `/mining/${currentSessionId}/close`
          : '/mining/current/close',
        label: t('MINING.CLOSE'),
      },
    ],
  },
  {
    id: 'sessions-list',
    linkTo: '/mining',
    label: t('MINING.SESSIONS_LIST'),
  },
];
