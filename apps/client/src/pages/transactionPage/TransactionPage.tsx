import MainLayout from '@/layouts/mainLayout/MainLayout';
import {
  SidebarLayout,
} from '@/layouts/sidebarLayout';
import { useTranslations } from '@/i18n/useTranslations';

import { transactionButtons } from './constants';
import TransactionContent from './TransactionContent';

/** Render the transactions workspace with inventory and transaction filters. */
export function TransactionPage() {
  const { t } = useTranslations();

  return (
    <MainLayout>
      <SidebarLayout
        buttons={transactionButtons(t)}
        defaultButtonId="owned"
        sidebarLabel={t('TRANSACTIONS.SIDEBAR_LABEL')}
      >
        <TransactionContent />
      </SidebarLayout>
    </MainLayout>
  );
}

export default TransactionPage;
