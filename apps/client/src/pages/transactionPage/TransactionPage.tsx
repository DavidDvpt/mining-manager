import MainLayout from '@/layouts/mainLayout/MainLayout';
import { SidebarLayout } from '@/layouts/sidebarLayout';
import { useTranslations } from '@/i18n/useTranslations';
import { useGetApiV1MaterialTypes } from '@/api/generated/miningManagerAPI';

import { transactionButtons } from './constants';
import TransactionContent from './TransactionContent';
import { useTransactionContext } from './transactionContext';
import { RunningTransactionsModal } from '@/shared/components';

/** Render the transactions workspace with inventory and transaction filters. */
export function TransactionPage() {
  const { t } = useTranslations();
  const { data: materialTypes = [] } = useGetApiV1MaterialTypes();
  const { context, updateContext } = useTransactionContext();
  const activePage = context.page ?? 'running-transactions';

  return (
    <MainLayout>
      <SidebarLayout
        buttons={transactionButtons(t, materialTypes)}
        defaultButtonId="running-transactions"
        activeButtonId={activePage}
        onButtonChange={(page) => {
          if (page === 'running-transactions') {
            updateContext({ modal: 'running-transactions' });
            return;
          }

          updateContext({
            page: page as typeof activePage,
            modal: null,
            type: null,
            item_id: null,
            lot_id: null,
          });
        }}
        sidebarLabel={t('TRANSACTIONS.SIDEBAR_LABEL')}
      >
        <TransactionContent
          materialTypes={materialTypes}
          context={context}
          updateContext={updateContext}
        />
      </SidebarLayout>
      <RunningTransactionsModal
        open={context.modal === 'running-transactions'}
        onOpenChange={(open) => {
          if (!open) updateContext({ modal: null });
        }}
      />
    </MainLayout>
  );
}

export default TransactionPage;
