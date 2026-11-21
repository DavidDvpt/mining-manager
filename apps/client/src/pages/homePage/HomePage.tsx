import { Panel, Section, SubSection } from '@/shared/components';
import { useTranslations } from '@/i18n/useTranslations';
import styles from './home-page.module.scss';

/** Render the authenticated information dashboard without showing running transactions. */
export function HomePage() {
  const { t } = useTranslations();

  return (
    <Panel className={styles.page}>
      <Section aria-labelledby="home-title">
        <h1 id="home-title">{t('APP.TITLE')}</h1>
        <SubSection>
          <p>{t('APP.HOME_DESCRIPTION')}</p>
        </SubSection>
      </Section>
    </Panel>
  );
}

export default HomePage;
