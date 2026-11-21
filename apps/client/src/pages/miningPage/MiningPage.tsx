import { SidebarLayout } from '@/layouts/sidebarLayout';
import { useTranslations } from '@/i18n/useTranslations';
import { Outlet, useLocation, useNavigate, useParams } from 'react-router-dom';

import { miningButtons } from './constants';
import type { MiningButtonId } from './constants';

/** Render the mining workspace shell and manage its sidebar navigation. */
export function MiningPage() {
  const { t } = useTranslations();
  const navigate = useNavigate();
  const location = useLocation();
  const { sessionId } = useParams<{ sessionId?: string }>();
  const isRunningRoute = location.pathname.endsWith('/running');
  const hasCurrentSession =
    Boolean(sessionId) || location.pathname.endsWith('/current');
  const activePage: MiningButtonId = location.pathname.endsWith('/create')
    ? 'create-session'
    : location.pathname.endsWith('/current') || isRunningRoute
      ? 'current-session'
      : sessionId && location.pathname.endsWith('/close')
        ? 'close'
        : sessionId
          ? 'current-session'
          : 'sessions-list';
  return (
    <SidebarLayout
      buttons={miningButtons(t, { hasCurrentSession })}
      defaultButtonId="sessions-list"
      activeButtonId={activePage}
      onButtonChange={(page) => {
        if (page === 'create-session') navigate('/mining/create');
        else if (page === 'current-session')
          navigate(
            sessionId && hasCurrentSession
              ? `/mining/${sessionId}/running`
              : '/mining/current',
          );
        else if (page === 'close' && sessionId)
          navigate(`/mining/${sessionId}/close`);
        else navigate('/mining');
      }}
      sidebarLabel={t('MINING.SIDEBAR_LABEL')}
    >
      <Outlet />
    </SidebarLayout>
  );
}

export default MiningPage;
