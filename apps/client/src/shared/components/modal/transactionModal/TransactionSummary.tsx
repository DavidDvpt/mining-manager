import { useWatch } from 'react-hook-form';
import {
  formatPercentageValue,
  formatRoundedDecimalValue,
} from '@/shared/utils';
import type {
  TransactionAction,
  TransactionFormValues,
} from '@/shared/types/modal';
import { useTranslations } from '@/i18n/useTranslations';
import { TransactionPricing } from './transactionPricing';
import styles from './transaction-modal.module.scss';

type TransactionSummaryProps = {
  stackable: boolean;
  action: TransactionAction;
  itemName: string;
};

/** Render the live action, quantity, and price totals using the existing pricing rules. */
export function TransactionSummary({
  stackable,
  action,
  itemName,
}: TransactionSummaryProps): import('react').JSX.Element {
  const values = useWatch<TransactionFormValues>();
  const { t } = useTranslations();
  const summary = TransactionPricing.summarize(
    {
      quantity: values.quantity ?? 1,
      tt: values.tt ?? 0,
      fee: values.fee ?? 0,
      ttc: values.ttc ?? 0,
    },
    action,
    stackable,
    values.purchase_quantity ?? 1,
  );
  return (
    <div className={styles.summary} aria-live="polite">
      <strong>
        {t(action === 'buy' ? 'ITEM_STORE.BUY' : 'ITEM_STORE.SELL')} ·{' '}
        {itemName}
      </strong>
      <div>
        <span>{t('TRANSACTION_MODAL.QUANTITY')}:</span>
        <span className={styles.value}>{summary.quantity}</span>
      </div>
      <div>
        <span>TT:</span>
        <span className={styles.value}>
          {formatRoundedDecimalValue(summary.tt)} PED
        </span>
      </div>
      <div>
        <span>{t('TRANSACTION_MODAL.FEE')}:</span>
        <span className={styles.value}>
          {formatRoundedDecimalValue(summary.fee)} PED
        </span>
      </div>
      <div>
        <span>{t('TRANSACTION_MODAL.TOTAL')} TTC:</span>
        <span className={styles.value}>
          {formatRoundedDecimalValue(summary.ttc)} PED
        </span>
      </div>
      {stackable ? (
        <>
          <div>
            <span>{t('TRANSACTION_MODAL.GROSS')}:</span>
            <span className={styles.value}>
              {formatPercentageValue(summary.gross)}%
            </span>
          </div>
          <div>
            <span>{t('TRANSACTION_MODAL.NET')}:</span>
            <span className={styles.value}>
              {formatPercentageValue(summary.net)}%
            </span>
          </div>
        </>
      ) : (
        <div>
          <span>{t('TRANSACTION_MODAL.MARKUP')}:</span>
          <span className={styles.value}>
            {formatRoundedDecimalValue(summary.markup)} PED
          </span>
        </div>
      )}
    </div>
  );
}

export default TransactionSummary;
