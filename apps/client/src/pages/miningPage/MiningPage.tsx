import { Outlet } from 'react-router-dom';
import { SidebarLayout } from '@/layouts/sidebarLayout';
import { useTranslations } from '@/i18n/useTranslations';
import { useGetApiV1MiningCurrent } from '@/api/generated/miningManagerAPI';
import { miningButtons } from './constants';

/** Render mining navigation, disabling creation while a session is open or unknown. */
export function MiningPage(): import('react').JSX.Element {
  const { t } = useTranslations();
  const current = useGetApiV1MiningCurrent();
  return (
    <SidebarLayout
      buttons={miningButtons(t, {
        currentSessionId: current.data?.id,
        hasCurrentSession:
          Boolean(current.data) || current.isPending || current.isError,
      })}
      sidebarLabel={t('MINING.SIDEBAR_LABEL')}
    >
      <Outlet />
    </SidebarLayout>
  );
}
export default MiningPage;
