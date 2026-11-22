import { GenericForm } from '@/shared/components/form/GenericForm';
import { FormButtonsSection } from '@/shared/components/form/FormButtonsSection';
import { Modal } from '@/shared/components/modal';
import type { TransactionModalProps } from '@/shared/types/modal';
import { TransactionModalInfo } from './TransactionModalInfo';
import { TransactionSummary } from './TransactionSummary';
import { transactionFormSchema } from './transactionFormSchema';
import styles from './transaction-modal.module.scss';

/** Render the shared transaction form shell around an action-specific form. */
export function TransactionModal({
  item,
  action,
  onClose,
  onSubmit,
  validationError = null,
  children,
}: TransactionModalProps): import('react').JSX.Element | null {
  if (!item) return null;

  const isStackable = Boolean(item.details.isStackable);

  return (
    <Modal
      open={true}
      onOpenChange={(nextOpen): void => {
        if (!nextOpen) onClose();
      }}
      title={action === 'buy' ? 'Achat' : 'Vente'}
      description={`${item.name} · ${isStackable ? 'Stackable' : 'Unstackable'}`}
    >
      <GenericForm
        key={item.id}
        schema={transactionFormSchema}
        defaultValues={{
          quantity: 1,
          tt: 0,
          fee: 0,
          ttc: 0,
          type_detail: 'AUCTION',
          purchase_quantity: 1,
        }}
        onSubmit={onSubmit}
        className={styles.form}
      >
        <TransactionModalInfo item={item} />
        {validationError ? (
          <p className={styles.validationError} role="alert">
            {validationError}
          </p>
        ) : null}
        {children}
        <TransactionSummary stackable={isStackable} />
        <FormButtonsSection
          onCancel={onClose}
          cancelLabel="Annuler"
          submitLabel="Valider"
          align="right"
        />
      </GenericForm>
    </Modal>
  );
}

export default TransactionModal;
