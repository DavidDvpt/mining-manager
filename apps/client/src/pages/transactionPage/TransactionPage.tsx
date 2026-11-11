import MainLayout from '@/layouts/mainLayout/MainLayout';
import {
  SidebarLayout,
} from '@/layouts/sidebarLayout';
import { useTranslations } from '@/i18n/useTranslations';
import { useGetApiV1MaterialTypes } from '@/api/generated/miningManagerAPI';

import { transactionButtons } from './constants';
import TransactionContent from './TransactionContent';

/** Render the transactions workspace with inventory and transaction filters. */
export function TransactionPage() {
  const { t } = useTranslations();
  const { data: materialTypes = [] } = useGetApiV1MaterialTypes();

  return (
    <MainLayout>
      <SidebarLayout
        buttons={transactionButtons(t, materialTypes)}
        defaultButtonId="finder"
        sidebarLabel={t('TRANSACTIONS.SIDEBAR_LABEL')}
      >
        <TransactionContent materialTypes={materialTypes} />
      </SidebarLayout>
    </MainLayout>
  );
}

export default TransactionPage;
