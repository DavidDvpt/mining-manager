import { GenericForm } from '@/shared/components/form/GenericForm';
import { FormButtonsSection } from '@/shared/components/form/FormButtonsSection';
import { Modal } from '@/shared/components/modal';
import { useQueryClient } from '@tanstack/react-query';
import {
  getGetApiV1ExcavatorsStockQueryKey,
  getGetApiV1FinderAmplifiersStockQueryKey,
  getGetApiV1FindersStockQueryKey,
  getGetApiV1RefinersStockQueryKey,
  getGetApiV1StorageMaterialMaterialIdStockQueryKey,
  getGetApiV1StorageMaterialStockQueryKey,
  usePostApiV1TransactionBuyStackable,
  usePostApiV1TransactionBuyUnstackable,
} from '@/api/generated/miningManagerAPI';
import type { TransactionFormValues } from '@/shared/types/modal';
import { TransactionBuyForm } from './TransactionBuyForm';
import { TransactionModalInfo } from '../TransactionModalInfo';
import { TransactionSummary } from '../TransactionSummary';
import {
  transactionFormSchema,
  TransactionFormType,
} from '../transactionFormSchema';
import { getTransactionKind } from '../transactionModal.utils';
import styles from '../transaction-modal.module.scss';
import type { ItemRow } from '@/shared/types';

type TransactionBuyModalProps = {
  item: ItemRow | null;
  onClose: () => void;
};

const initValues: TransactionFormType = {
  quantity: 1,
  tt: 0,
  fee: 0,
  ttc: 0,
  type_detail: 'AUCTION',
  purchase_quantity: 1,
};
/** Render and submit a buy transaction without any sell or lot-specific concerns. */
export function TransactionBuyModal({
  item,
  onClose,
}: TransactionBuyModalProps): import('react').JSX.Element | null {
  const queryClient = useQueryClient();
  const buyStackable = usePostApiV1TransactionBuyStackable();
  const buyUnstackable = usePostApiV1TransactionBuyUnstackable();
  const isStackable = Boolean(item?.details.isStackable);

  /** Validate and persist the buy request matching the item's stackability. */
  const handleSubmit = async (
    formValues: TransactionFormValues,
  ): Promise<void> => {
    if (!item) return;

    let queryKeys = [];
    const kind = getTransactionKind(item);

    if (isStackable && item.stock === null) {
      throw new Error('Stackable buy requires item stock.');
    }

    if (isStackable) {
      await buyStackable.mutateAsync({
        data: {
          quantity: formValues.quantity,
          kind,
          type_detail: formValues.type_detail,
          item_id: item.id,
          fee: formValues.fee,
          ttc: formValues.ttc,
        },
      });

      queryKeys = [
        getGetApiV1StorageMaterialStockQueryKey(),
        getGetApiV1StorageMaterialMaterialIdStockQueryKey(item.id),
      ];
    } else {
      await buyUnstackable.mutateAsync({
        data: {
          quantity: 1,
          purchase_quantity: formValues.purchase_quantity,
          kind,
          type_detail: formValues.type_detail,
          item_id: item.id,
          tt: formValues.tt,
          fee: formValues.fee,
          ttc: formValues.ttc,
        },
      });

      queryKeys = [
        getGetApiV1FindersStockQueryKey(),
        getGetApiV1ExcavatorsStockQueryKey(),
        getGetApiV1RefinersStockQueryKey(),
        getGetApiV1FinderAmplifiersStockQueryKey(),
      ];
    }

    await Promise.all(
      queryKeys.map((queryKey): Promise<void> =>
        queryClient.invalidateQueries({ queryKey }),
      ),
    );

    onClose();
  };

  if (!item) return null;

  return (
    <Modal
      open={true}
      onOpenChange={(nextOpen): void => {
        if (!nextOpen) onClose();
      }}
      title="Achat"
      description={`${item.name} · ${isStackable ? 'Stackable' : 'Unstackable'}`}
    >
      <GenericForm
        key={item.id}
        schema={transactionFormSchema}
        defaultValues={initValues}
        onSubmit={handleSubmit}
        className={styles.form}
      >
        <TransactionModalInfo item={item} />

        <TransactionBuyForm isStackable={isStackable} item={item} />

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

export default TransactionBuyModal;
