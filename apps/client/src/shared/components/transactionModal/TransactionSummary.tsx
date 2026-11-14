import { useWatch } from 'react-hook-form';
import { formatDecimalValue, formatPercentageValue } from '@/shared/utils';
import type { TransactionFormValues } from '@/shared/types/modal';
import styles from './transaction-modal.module.scss';

type TransactionSummaryProps = {
  stackable: boolean;
};

/** Render the live transaction summary from React Hook Form values. */
export function TransactionSummary({ stackable }: TransactionSummaryProps) {
  const formValues = useWatch<TransactionFormValues>();
  const quantity = formValues.quantity ?? 1;
  const tt = formValues.tt ?? 0;
  const fee = formValues.fee ?? 0;
  const ttc = formValues.ttc ?? 0;
  const totalTt = stackable ? tt * quantity : tt;

  if (stackable) {
    const gross = totalTt > 0 ? (ttc / totalTt) * 100 : 0;
    const net = totalTt > 0 ? ((ttc - fee) / totalTt) * 100 : 0;
    return (
      <div className={styles.summary}>
        <span>TT total</span>
        <strong>{formatDecimalValue(totalTt)}</strong>
        <span>Brut</span>
        <strong>{formatPercentageValue(gross)}%</strong>
        <span>Net</span>
        <strong>{formatPercentageValue(net)}%</strong>
      </div>
    );
  }

  return (
    <div className={styles.summary}>
      <span>TT total</span>
      <strong>{formatDecimalValue(totalTt)}</strong>
      <span>Plus-value</span>
      <strong>{formatDecimalValue(ttc - totalTt)}</strong>
    </div>
  );
}

export default TransactionSummary;
