import { useTranslations } from '@/i18n/useTranslations';
import { Outlet, useLocation, useParams } from 'react-router-dom';

import MiningSessionForm from './createSession';
import { getMiningActiveView } from './utils';
import type { MiningButtonId } from './constants';
import MiningSessionsList from './sessionsList';

/** Render the main mining panel selected by the current route. */
export function MiningPageContent(): import('react').JSX.Element {
  const { t } = useTranslations();
  const location = useLocation();
  const { sessionId } = useParams<{ sessionId?: string }>();
  const isRunningRoute = location.pathname.endsWith('/running');
  const activePage: MiningButtonId = location.pathname.endsWith('/create')
    ? 'create-session'
    : location.pathname.endsWith('/current') || isRunningRoute
      ? 'current-session'
      : sessionId && location.pathname.endsWith('/close')
        ? 'close'
        : sessionId
          ? 'current-session'
          : 'sessions-list';

  if (activePage === 'create-session') return <MiningSessionForm />;

  return <MiningSessionsList activeView={getMiningActiveView(activePage, t)} />;
}

/** Provide a route boundary for a mining session and its future child views. */
export function MiningSessionRoute(): import('react').JSX.Element {
  return <Outlet />;
}

export default MiningPageContent;
