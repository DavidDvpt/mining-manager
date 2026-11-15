import MainLayout from '@/layouts/mainLayout/MainLayout';
import { SidebarLayout } from '@/layouts/sidebarLayout';
import { useTranslations } from '@/i18n/useTranslations';
import { Panel, Section, SubSection } from '@/shared/components';

import { miningButtons } from './constants';
import MiningSessionForm from './MiningSessionForm';
import { useMiningContext } from './miningContext';
import styles from './mining-page.module.scss';
import { getMiningActivePage, getMiningActiveView } from './utils';

/** Render the mining workspace with its current-session and session-list navigation. */
export function MiningPage() {
  const { t } = useTranslations();
  const { context, updateContext } = useMiningContext();
  const hasCurrentSession = Boolean(context.session_id);
  const activePage = getMiningActivePage(context.page, hasCurrentSession);
  const activeView = getMiningActiveView(activePage, t);
  const [activeViewPrefix, activeViewSuffix] = t('MINING.ACTIVE_VIEW').split(
    '{view}',
  );

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
          <Panel className={styles.page}>
            <>
              <Section className={styles.loots} aria-labelledby="mining-title">
                <h1 id="mining-title">{t('MINING.LOOTS')}</h1>
                <SubSection>
                  <p>
                    {activeViewPrefix}
                    <span className={styles.activeView}>{activeView}</span>
                    {activeViewSuffix}
                  </p>
                  <p>{t('MINING.DESCRIPTION')}</p>
                </SubSection>
              </Section>
              <Section
                className={styles.cockpit}
                aria-labelledby="cockpit-title"
              >
                <h2 id="cockpit-title">{t('MINING.COCKPIT')}</h2>
              </Section>
            </>
          </Panel>
        )}
      </SidebarLayout>
    </MainLayout>
  );
}

export default MiningPage;
