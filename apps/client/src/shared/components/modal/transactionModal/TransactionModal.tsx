import { GenericForm } from '@/shared/components/form/GenericForm';
import { FormButtonsSection } from '@/shared/components/form/FormButtonsSection';
import { Modal } from '@/shared/components/modal';
import { useTranslations } from '@/i18n/useTranslations';
import { useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import {
  getGetApiV1StorageMaterialStockQueryKey,
  usePostApiV1TransactionBuyStackable,
  usePostApiV1TransactionBuyUnstackable,
  usePostApiV1TransactionSellStackable,
  usePostApiV1TransactionSellUnstackable,
} from '@/api/generated/miningManagerAPI';
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
}: TransactionModalProps) {
  const { t } = useTranslations();
  const queryClient = useQueryClient();
  const [validationError, setValidationError] = useState<string | null>(null);
  const buyStackable = usePostApiV1TransactionBuyStackable();
  const buyUnstackable = usePostApiV1TransactionBuyUnstackable();
  const sellStackable = usePostApiV1TransactionSellStackable();
  const sellUnstackable = usePostApiV1TransactionSellUnstackable();
  const isStackable = Boolean(item && isStackableItem(item) && !lot);

  /** Persist the transaction through the mutation matching its action and stackability. */
  const handleSubmit = async (formValues: TransactionFormValues) => {
    if (!item) return;

    if (action === 'sell' && isStackable && formValues.quantity > (item.stock ?? 0)) {
      setValidationError(t('TRANSACTIONS.QUANTITY_EXCEEDS_STOCK'));
      return;
    }

    if (
      action === 'sell' &&
      !isStackable &&
      formValues.tt > (item.tt ?? 0)
    ) {
      setValidationError(t('TRANSACTIONS.TT_EXCEEDS_BASE'));
      return;
    }

    setValidationError(null);

    const kind = item.kind === 'material'
      ? 'material'
      : item.kind === 'enhancer'
        ? 'enhancer'
        : 'tool';

    if (action === 'sell') {
      if (isStackable) {
        await sellStackable.mutateAsync({
          data: {
            quantity: formValues.quantity,
            item_id: item.id,
            tt: formValues.tt,
            ttc: formValues.ttc,
          },
        });
      } else if (lot) {
        await sellUnstackable.mutateAsync({
          data: {
            quantity: 1,
            lot_id: lot.id,
            tt: formValues.tt,
            ttc: formValues.ttc,
          },
        });
      }
    } else if (isStackable) {
      await buyStackable.mutateAsync({
        data: {
          quantity: formValues.quantity,
          kind,
          type_detail: 'TT',
          item_id: item.id,
          fee: formValues.fee,
          ttc: formValues.ttc,
        },
      });
    } else {
      await buyUnstackable.mutateAsync({
        data: {
          quantity: 1,
          kind,
          type_detail: 'TT',
          item_id: item.id,
          tt: formValues.tt,
          fee: formValues.fee,
          ttc: formValues.ttc,
        },
      });
    }

    if (item.kind === 'material' && isStackable) {
      const stockDelta = action === 'buy' ? formValues.quantity : -formValues.quantity;
      const stockQueryKey = getGetApiV1StorageMaterialStockQueryKey();
      queryClient.setQueryData<Record<string, number>>(
        stockQueryKey,
        (stock = {}) => ({
          ...stock,
          [item.id]: Math.max(0, (stock[item.id] ?? item.stock ?? 0) + stockDelta),
        }),
      );
    }

    onOpenChange(false);
  };

  if (!item) return null;

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
        defaultValues={{
          quantity: 1,
          tt: 0,
          fee: 0,
          ttc: 0,
          autoCompute: true,
        }}
        onSubmit={handleSubmit}
        className={styles.form}
      >
        <TransactionModalInfo item={item} lot={lot} />
        {validationError ? (
          <p className={styles.validationError} role="alert">
            {validationError}
          </p>
        ) : null}
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
