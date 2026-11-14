import { GenericForm } from '@/shared/components/form/GenericForm';
import { FormButtonsSection } from '@/shared/components/form/FormButtonsSection';
import { Modal } from '@/shared/components/modal';
import { isStackableItem } from '@/shared/utils';
import type {
  TransactionFormValues,
  TransactionModalProps,
} from '@/shared/types/modal';
import { TransactionForm } from './TransactionForm';
import { TransactionModalInfo } from './TransactionModalInfo';
import { TransactionSummary } from './TransactionSummary';
import { transactionFormSchema } from './transactionFormSchema';
import styles from './transaction-modal.module.scss';

/** Render the transaction modal and orchestrate its pricing form. */
export function TransactionModal({
  item,
  lot,
  action,
  open,
  onOpenChange,
  onSubmit,
}: TransactionModalProps) {
  /** Submit normalized values received from React Hook Form. */
  const handleSubmit = async (formValues: TransactionFormValues) => {
    await onSubmit?.({
      quantity: formValues.quantity,
      tt: formValues.tt,
      fee: formValues.fee,
      ttc: formValues.ttc,
      auction: formValues.auction,
    });
    onOpenChange(false);
  };

  if (!item) return null;

  const isStackable = isStackableItem(item);
  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={action === 'buy' ? 'Achat' : 'Vente'}
      description={`${item.name} · ${isStackable ? 'Stackable' : 'Unstackable'}`}
    >
      <GenericForm
        key={`${item.id}-${lot?.id ?? 'new'}-${open}`}
        schema={transactionFormSchema}
        defaultValues={{ quantity: 1, tt: 0, fee: 0, ttc: 0, auction: true }}
        onSubmit={handleSubmit}
        className={styles.form}
      >
        <TransactionModalInfo item={item} lot={lot} />
        <TransactionForm
          action={action}
          isStackable={isStackable}
          item={item}
          lot={lot}
        />
        <TransactionSummary stackable={isStackable} />
        <FormButtonsSection
          onCancel={() => onOpenChange(false)}
          cancelLabel="Annuler"
          submitLabel="Valider"
          align="right"
        />
      </GenericForm>
    </Modal>
  );
}

export default TransactionModal;
