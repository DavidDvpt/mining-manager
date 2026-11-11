import { useTranslations } from '@/i18n/useTranslations';
import { useSidebarLayoutContext } from '@/layouts/sidebarLayout';
import { Panel, Section } from '@/shared/components';
import type { MaterialTypeResponse } from '@/api/generated/model/materialTypeResponse';

import { FIXED_TRANSACTION_BUTTONS } from './constants';
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
  const fixedButton = FIXED_TRANSACTION_BUTTONS.find(
    ({ id }) => id === activeButtonId,
  );
  const materialType = materialTypes.find(
    ({ id }) => `material-type-${id}` === activeButtonId,
  );
  const activeView =
    fixedButton?.label ??
    (activeButtonId === 'materials'
      ? t('TRANSACTIONS.MATERIALS')
      : activeButtonId === 'running-transactions'
        ? t('TRANSACTIONS.RUNNING_TRANSACTIONS')
      : materialType?.name ?? activeButtonId);
  const [activeViewPrefix, activeViewSuffix] = t('TRANSACTIONS.ACTIVE_VIEW').split(
    '{view}',
  );

  return (
    <Panel className={styles.page}>
      <Section>
        <h1>{t('TRANSACTIONS.TITLE')}</h1>
        <p>
          {activeViewPrefix}
          <span className={styles.activeView}>{activeView}</span>
          {activeViewSuffix}
        </p>
        <p>{t('TRANSACTIONS.DESCRIPTION')}</p>
      </Section>
    </Panel>
  );
}

export default TransactionContent;
