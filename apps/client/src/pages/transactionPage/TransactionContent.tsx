import { useTranslations } from '@/i18n/useTranslations';
import { useSidebarLayoutContext } from '@/layouts/sidebarLayout';
import { Panel, Section } from '@/shared/components';

import styles from './transaction-page.module.scss';

/** Render the transaction content using the selection supplied by the sidebar context. */
export function TransactionContent() {
  const { activeButtonId } = useSidebarLayoutContext();
  const { t } = useTranslations();
  const activeViewLabels: Record<string, string> = {
    owned: t('TRANSACTIONS.OWNED'),
    tools: t('TRANSACTIONS.TOOLS'),
    accessories: t('TRANSACTIONS.ACCESSORIES'),
    materials: t('TRANSACTIONS.MATERIALS'),
    'materials-ores': t('TRANSACTIONS.ORES'),
    'materials-enmat': t('TRANSACTIONS.ENMAT'),
    'materials-refined': t('TRANSACTIONS.REFINED'),
  };

  return (
    <Panel className={styles.page}>
      <Section>
        <h1>{t('TRANSACTIONS.TITLE')}</h1>
        <p>
          {t('TRANSACTIONS.ACTIVE_VIEW').replace(
            '{view}',
            activeViewLabels[activeButtonId] ?? activeButtonId,
          )}
        </p>
        <p>{t('TRANSACTIONS.DESCRIPTION')}</p>
      </Section>
    </Panel>
  );
}

export default TransactionContent;
