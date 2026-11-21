import { Panel, Section, SubSection } from '@/shared/components';
import { useTranslations } from '@/i18n/useTranslations';

import styles from './mining-sessions-list.module.scss';

type MiningSessionsListProps = {
  activeView: string;
};

/** Render the mining sessions list view and its current placeholder panels. */
export function MiningSessionsList({
  activeView,
}: MiningSessionsListProps): import('react').JSX.Element {
  const { t } = useTranslations();
  const [activeViewPrefix, activeViewSuffix] =
    t('MINING.ACTIVE_VIEW').split('{view}');

  return (
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
        <Section className={styles.cockpit} aria-labelledby="cockpit-title">
          <h2 id="cockpit-title">{t('MINING.COCKPIT')}</h2>
        </Section>
      </>
    </Panel>
  );
}

export default MiningSessionsList;
