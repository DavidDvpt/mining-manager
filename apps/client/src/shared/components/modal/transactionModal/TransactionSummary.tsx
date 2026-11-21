import { useWatch } from 'react-hook-form';
import {
  formatPercentageValue,
  formatRoundedDecimalValue,
} from '@/shared/utils';
import type { TransactionFormValues } from '@/shared/types/modal';
import styles from './transaction-modal.module.scss';

type TransactionSummaryProps = {
  stackable: boolean;
};

/** Render the live transaction summary from React Hook Form values. */
export function TransactionSummary({
  stackable,
}: TransactionSummaryProps): import('react').JSX.Element {
  const formValues = useWatch<TransactionFormValues>();
  const tt = formValues.tt ?? 0;
  const fee = formValues.fee ?? 0;
  const ttc = formValues.ttc ?? 0;

  if (stackable) {
    const gross = tt > 0 ? (ttc / tt) * 100 : 0;
    const net = tt > 0 ? ((ttc - fee) / tt) * 100 : 0;
    return (
      <div className={styles.summary}>
        <div>
          <span>Brut:</span>
          <span className={styles.value}>{formatPercentageValue(gross)}%</span>
        </div>
        <div>
          <span>Net:</span>
          <span className={styles.value}>{formatPercentageValue(net)}%</span>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.summary}>
      <div>
        <span>Plus-value</span>
        <span className={styles.value}>
          {formatRoundedDecimalValue(ttc - tt)} Peds
        </span>
      </div>
    </div>
  );
}

export default TransactionSummary;
