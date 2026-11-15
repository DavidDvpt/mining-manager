import MainLayout from '@/layouts/mainLayout/MainLayout';
import { SidebarLayout } from '@/layouts/sidebarLayout';
import { useTranslations } from '@/i18n/useTranslations';

import { miningButtons } from './constants';
import MiningSessionForm from './createSession';
import { useMiningContext } from './miningContext';
import MiningSessionsList from './sessionsList';
import { getMiningActivePage, getMiningActiveView } from './utils';

/** Render the mining workspace with its current-session and session-list navigation. */
export function MiningPage() {
  const { t } = useTranslations();
  const { context, updateContext } = useMiningContext();
  const hasCurrentSession = Boolean(context.session_id);
  const activePage = getMiningActivePage(context.page, hasCurrentSession);
  const activeView = getMiningActiveView(activePage, t);
  return (
    <MainLayout>
      <SidebarLayout
        buttons={miningButtons(t, { hasCurrentSession })}
        defaultButtonId="sessions-list"
        activeButtonId={activePage}
        onButtonChange={(page) =>
          updateContext({ page: page as typeof activePage })
        }
        sidebarLabel={t('MINING.SIDEBAR_LABEL')}
      >
        {activePage === 'create-session' ? (
          <MiningSessionForm />
        ) : (
          <MiningSessionsList activeView={activeView} />
        )}
      </SidebarLayout>
    </MainLayout>
  );
}

export default MiningPage;
