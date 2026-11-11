import { useTranslations } from '@/i18n/useTranslations';
import { useSidebarLayoutContext } from '@/layouts/sidebarLayout';
import { Panel, Section } from '@/shared/components';
import type { MaterialTypeResponse } from '@/api/generated/model/materialTypeResponse';

import styles from './transaction-page.module.scss';

type TransactionContentProps = {
  materialTypes?: MaterialTypeResponse[];
};

/** Render transaction content using the sidebar selection and loaded material types. */
export function TransactionContent({
  materialTypes = [],
}: TransactionContentProps) {
  const { activeButtonId } = useSidebarLayoutContext();
  const { t } = useTranslations();
  const activeViewLabels: Record<string, string> = {
    owned: t('TRANSACTIONS.OWNED'),
    tools: t('TRANSACTIONS.TOOLS'),
    accessories: t('TRANSACTIONS.ACCESSORIES'),
    materials: t('TRANSACTIONS.MATERIALS'),
  };
  const materialType = materialTypes.find(
    ({ id }) => `material-type-${id}` === activeButtonId,
  );

  return (
    <Panel className={styles.page}>
      <Section>
        <h1>{t('TRANSACTIONS.TITLE')}</h1>
        <p>
          {t('TRANSACTIONS.ACTIVE_VIEW').replace(
            '{view}',
            activeViewLabels[activeButtonId] ?? materialType?.name ?? activeButtonId,
          )}
        </p>
        <p>{t('TRANSACTIONS.DESCRIPTION')}</p>
      </Section>
    </Panel>
  );
}

export default TransactionContent;
