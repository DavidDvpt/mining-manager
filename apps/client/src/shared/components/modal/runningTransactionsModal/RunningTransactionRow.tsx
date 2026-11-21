import type {
  RunningTransactionResponse,
  UpdateTransactionStatusRequestStatus,
} from '@/api/generated/model';
import { UpdateTransactionStatusRequestStatus as Status } from '@/api/generated/model';
import { getItemImageUrl } from '@/config/images';
import type { TranslationKey } from '@/i18n/types';
import { EntropiaImage } from '@/shared/components/entropiaImage';
import { formatDecimalValue } from '@/shared/utils';
import type { ItemColumn } from '@/shared/types/listItem';
import styles from './running-transactions-modal.module.scss';

export type RunningTransactionRow = RunningTransactionResponse & { id: string };
type Translate = (key: TranslationKey) => string;

/** Convert the generated transaction response to the generic AppList row shape. */
export function toRunningTransactionRow(
  transaction: RunningTransactionResponse,
): RunningTransactionRow {
  return { ...transaction, id: transaction.sessionId };
}

/** Format the API date for the running transaction list. */
function formatTransactionDate(value: string): string {
  return new Date(value).toLocaleDateString('fr-FR');
}

/** Create the shared AppList columns for running transaction rows. */
export function createRunningTransactionColumns(
  t: Translate,
  onStatusChange: (
    row: RunningTransactionRow,
    status: UpdateTransactionStatusRequestStatus,
  ) => void,
): ItemColumn<RunningTransactionRow>[] {
  const statusOptions = Object.values(Status).map(
    (
      status,
    ): {
      label: 'RUNNING' | 'SOLDED' | 'RETURNED' | 'CANCELLED';
      value: 'RUNNING' | 'SOLDED' | 'RETURNED' | 'CANCELLED';
    } => ({
      label: status,
      value: status,
    }),
  );

  return [
    {
      key: 'image',
      label: '',
      flex: '0 0 4rem',
      render: (row): import('react').JSX.Element => (
        <EntropiaImage
          url={getItemImageUrl(row.item.imgId)}
          alt={row.item.name}
          size="small"
        />
      ),
    },
    {
      key: 'name',
      label: t('RUNNING_TRANSACTIONS_MODAL.NAME'),
      flex: '1 1 14rem',
      render: (row): string => row.item.name,
    },
    {
      key: 'quantity',
      label: t('RUNNING_TRANSACTIONS_MODAL.QUANTITY'),
      flex: '0 1 6rem',
      align: 'right',
      render: (row): number => row.quantity,
    },
    {
      key: 'createdAt',
      label: t('RUNNING_TRANSACTIONS_MODAL.CREATED_AT'),
      flex: '0 1 8rem',
      render: (row): string => formatTransactionDate(row.createdAt),
    },
    {
      key: 'tt',
      label: 'TT',
      flex: '0 1 6rem',
      align: 'right',
      render: (row): string => formatDecimalValue(row.tt),
    },
    {
      key: 'ttc',
      label: 'TTC',
      flex: '0 1 6rem',
      align: 'right',
      render: (row): string => formatDecimalValue(row.ttc),
    },
    {
      key: 'status',
      label: t('RUNNING_TRANSACTIONS_MODAL.STATUS'),
      kind: 'select',
      flex: '0 0 11rem',
      cellClassName: styles.statusCell,
      selectOptions: statusOptions,
      selectValue: (
        row,
      ): import('@/api/generated/model').RunningTransactionResponseStatus =>
        row.status,
      onSelectChange: (row, value): void =>
        onStatusChange(row, value as UpdateTransactionStatusRequestStatus),
      render: (): null => null,
    },
  ];
}
