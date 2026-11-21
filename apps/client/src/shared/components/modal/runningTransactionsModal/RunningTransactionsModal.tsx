import { useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { AppList } from '@/shared/appList';
import { Modal } from '@/shared/components/modal';
import {
  getGetApiV1TransactionRunningQueryKey,
  useGetApiV1TransactionRunning,
  usePatchApiV1TransactionSessionIdStatus,
} from '@/api/generated/miningManagerAPI';
import type { UpdateTransactionStatusRequestStatus } from '@/api/generated/model';
import { useTranslations } from '@/i18n/useTranslations';
import styles from './running-transactions-modal.module.scss';
import {
  createRunningTransactionColumns,
  toRunningTransactionRow,
  type RunningTransactionRow,
} from './RunningTransactionRow';

type RunningTransactionsModalProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

/** Display running transactions through the shared generic AppList. */
export function RunningTransactionsModal({
  open,
  onOpenChange,
}: RunningTransactionsModalProps): import('react').JSX.Element {
  const { t } = useTranslations();
  const queryClient = useQueryClient();
  const transactions = useGetApiV1TransactionRunning({
    query: {
      enabled: open,
      queryKey: getGetApiV1TransactionRunningQueryKey(),
    },
  });
  const updateStatus = usePatchApiV1TransactionSessionIdStatus();
  const rows = useMemo(
    (): RunningTransactionRow[] =>
      (transactions.data ?? []).map(toRunningTransactionRow),
    [transactions.data],
  );
  const queryKey = getGetApiV1TransactionRunningQueryKey();

  /** Update a running transaction and invalidate its list query. */
  const handleStatusChange = async (
    row: RunningTransactionRow,
    status: UpdateTransactionStatusRequestStatus,
  ): Promise<void> => {
    if (status === row.status) return;
    await updateStatus.mutateAsync({
      sessionId: row.sessionId,
      data: { status },
    });
    await queryClient.invalidateQueries({ queryKey });
  };

  const columns = useMemo(
    (): import('../../..').ItemStoreColumn<RunningTransactionRow>[] =>
      createRunningTransactionColumns(t, (row, status): void => {
        void handleStatusChange(row, status);
      }),
    [t],
  );
  const tools = rows.filter(({ kind }): boolean => kind === 'tool');
  const resources = rows.filter(({ kind }): boolean => kind === 'resource');

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={t('RUNNING_TRANSACTIONS_MODAL.TITLE')}
      className={styles.modal}
    >
      <div className={styles.content}>
        {tools.length && (
          <section>
            <h2>{t('RUNNING_TRANSACTIONS_MODAL.TOOLS')}</h2>
            <AppList
              columns={columns}
              rows={tools}
              isLoading={transactions.isLoading}
              isError={transactions.isError}
              loadingMessage={t('RUNNING_TRANSACTIONS_MODAL.LOADING')}
              errorMessage={t('RUNNING_TRANSACTIONS_MODAL.ERROR')}
              emptyMessage={t('RUNNING_TRANSACTIONS_MODAL.EMPTY')}
            />
          </section>
        )}
        {resources.length && (
          <section>
            <h2>{t('RUNNING_TRANSACTIONS_MODAL.RESOURCES')}</h2>
            <AppList
              columns={columns}
              rows={resources}
              isLoading={transactions.isLoading}
              isError={transactions.isError}
              loadingMessage={t('RUNNING_TRANSACTIONS_MODAL.LOADING')}
              errorMessage={t('RUNNING_TRANSACTIONS_MODAL.ERROR')}
              emptyMessage={t('RUNNING_TRANSACTIONS_MODAL.EMPTY')}
            />
          </section>
        )}
      </div>
    </Modal>
  );
}

export default RunningTransactionsModal;
