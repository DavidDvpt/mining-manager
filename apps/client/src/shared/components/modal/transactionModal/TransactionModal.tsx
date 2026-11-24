import { useMemo, useRef, useState } from 'react';
import { GenericForm } from '@/shared/components/form/GenericForm';
import { FormButtonsSection } from '@/shared/components/form/FormButtonsSection';
import { Modal } from '@/shared/components/modal';
import type {
  TransactionFormValues,
  TransactionModalProps,
} from '@/shared/types/modal';
import { useTranslations } from '@/i18n/useTranslations';
import { TransactionModalInfo } from './TransactionModalInfo';
import { TransactionSummary } from './TransactionSummary';
import { TransactionForm } from './TransactionForm';
import { transactionFormSchema } from './transactionFormSchema';
import styles from './transaction-modal.module.scss';

/** Own the validated transaction form, selected lot pricing, submission lock, and recoverable errors. */
export function TransactionModal({
  item,
  lot,
  stock,
  action,
  onClose,
  onSubmit,
}: TransactionModalProps): import('react').JSX.Element {
  const { t } = useTranslations();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const submitting = useRef(false);
  const isStackable = Boolean(item.details.isStackable);
  const pricingItem = useMemo(
    () => (lot ? { ...item, ttRemaining: lot.tt } : item),
    [item, lot],
  );
  const schema = useMemo(
    () =>
      transactionFormSchema.superRefine((values, context): void => {
        if (
          action === 'sell' &&
          isStackable &&
          stock !== undefined &&
          values.quantity > stock
        ) {
          context.addIssue({
            code: 'custom',
            path: ['quantity'],
            message: t('TRANSACTIONS.QUANTITY_EXCEEDS_STOCK'),
          });
        }
        if (action === 'sell' && !isStackable && values.tt > (item.tt ?? 0)) {
          context.addIssue({
            code: 'custom',
            path: ['tt'],
            message: t('TRANSACTIONS.TT_EXCEEDS_BASE'),
          });
        }
      }),
    [action, isStackable, stock, item.tt, t],
  );

  /** Keep the workflow open during submission so an in-flight mutation cannot be submitted twice. */
  const close = (): void => {
    if (!submitting.current) onClose();
  };

  /** Submit once, display mutation failures, and preserve the draft for a retry. */
  const submit = async (values: TransactionFormValues): Promise<void> => {
    if (submitting.current) return;
    submitting.current = true;
    setPending(true);
    setError(null);
    try {
      await onSubmit(values);
    } catch (failure) {
      setError(
        failure instanceof Error
          ? failure.message
          : t('TRANSACTION_MODAL.SUBMIT_ERROR'),
      );
    } finally {
      submitting.current = false;
      setPending(false);
    }
  };

  return (
    <Modal
      open
      onOpenChange={(open): void => {
        if (!open) close();
      }}
      title={t(action === 'buy' ? 'ITEM_STORE.BUY' : 'ITEM_STORE.SELL')}
      description={item.name}
    >
      <GenericForm
        key={`${action}:${lot?.id ?? item.id}`}
        schema={schema}
        defaultValues={{
          quantity: 1,
          tt: 0,
          fee: 0,
          ttc: 0,
          type_detail: 'AUCTION',
          purchase_quantity: 1,
          autoCompute: action === 'sell',
        }}
        onSubmit={submit}
        className={styles.form}
      >
        <TransactionModalInfo
          item={pricingItem}
          tier={lot?.tier}
          stock={stock}
        />
        {error ? (
          <p className={styles.validationError} role="alert">
            {error}
          </p>
        ) : null}
        <fieldset disabled={pending} className={styles.formFields}>
          <TransactionForm
            action={action}
            isStackable={isStackable}
            item={pricingItem}
          />
        </fieldset>
        <TransactionSummary
          stackable={isStackable}
          action={action}
          itemName={
            lot?.tier != null ? `${item.name} · T${lot.tier}` : item.name
          }
        />
        <FormButtonsSection
          onCancel={close}
          cancelLabel={t('TOOL_EDIT_MODAL.CANCEL')}
          submitLabel={t('TRANSACTION_MODAL.CONFIRM')}
          submitDisabled={pending}
          cancelDisabled={pending}
          align="right"
        />
      </GenericForm>
    </Modal>
  );
}

export default TransactionModal;
