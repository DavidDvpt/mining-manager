import { Outlet, useLocation } from 'react-router-dom';
import { useTranslations } from '@/i18n/useTranslations';
import MiningSessionsList from './sessionsList';

/** Keep the mining panel mounted behind route-controlled creation modals. */
export function MiningPageContent(): import('react').JSX.Element {
  const { t } = useTranslations();
  const { pathname } = useLocation();
  return (
    <>
      <MiningSessionsList
        activeView={t(
          pathname.endsWith('/running') || pathname.endsWith('/current')
            ? 'MINING.CURRENT_SESSION'
            : 'MINING.SESSIONS_LIST',
        )}
      />
      <Outlet />
    </>
  );
}
export default MiningPageContent;
