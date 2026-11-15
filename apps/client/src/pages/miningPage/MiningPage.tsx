import MainLayout from '@/layouts/mainLayout/MainLayout';
import { SidebarLayout } from '@/layouts/sidebarLayout';
import { useTranslations } from '@/i18n/useTranslations';
import { Panel, Section, SubSection } from '@/shared/components';

import { miningButtons } from './constants';
import { useMiningContext } from './miningContext';
import styles from './mining-page.module.scss';

/** Render the mining workspace with its current-session and session-list navigation. */
export function MiningPage() {
  const { t } = useTranslations();
  const { context, updateContext } = useMiningContext();
  const activePage = context.page ?? 'sessions-list';
  const activeView =
    activePage === 'current-session'
      ? t('MINING.CURRENT_SESSION')
      : activePage === 'sessions-list'
        ? t('MINING.SESSIONS_LIST')
        : t('MINING.CLOSE');
  const [activeViewPrefix, activeViewSuffix] = t('MINING.ACTIVE_VIEW').split(
    '{view}',
  );

  return (
    <MainLayout>
      <SidebarLayout
        buttons={miningButtons(t)}
        defaultButtonId="sessions-list"
        activeButtonId={activePage}
        onButtonChange={(page) => updateContext({ page: page as typeof activePage })}
        sidebarLabel={t('MINING.SIDEBAR_LABEL')}
      >
        <Panel className={styles.page}>
          <Section aria-labelledby="mining-title">
            <h1 id="mining-title">{t('MINING.TITLE')}</h1>
            <SubSection>
              <p>
                {activeViewPrefix}
                <span className={styles.activeView}>{activeView}</span>
                {activeViewSuffix}
              </p>
              <p>{t('MINING.DESCRIPTION')}</p>
            </SubSection>
          </Section>
        </Panel>
      </SidebarLayout>
    </MainLayout>
  );
}

export default MiningPage;
