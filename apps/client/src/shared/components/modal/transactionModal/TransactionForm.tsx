import { JSX, useCallback, useEffect, useMemo, useRef } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';
import { CheckboxRHF } from '@/shared/components/form/CheckboxRHF';
import type {
  TransactionAction,
  TransactionFormValues,
  TransactionItem,
} from '@/shared/types/modal';
import {
  TransactionPricing,
  type TransactionPricingValues,
} from './transactionPricing';
import styles from './transaction-modal.module.scss';
import { useTranslations } from '@/i18n/useTranslations';
import { TransactionInputs } from './TransactionInputs';
import { TransactionTypeAndQuantityFields } from './TransactionTypeAndQuantityFields';

type TransactionFormProps = {
  isStackable: boolean;
  item: TransactionItem | null;
  action: TransactionAction;
};

/** Render transaction fields and synchronize pricing according to the action. */
export function TransactionForm({
  isStackable,
  item,
  action,
}: TransactionFormProps): JSX.Element {
  const pricingRef = useRef<TransactionPricing | null>(null);
  const { setValue, getValues } = useFormContext<TransactionFormValues>();
  const { t } = useTranslations();
  const autoCompute = useWatch<TransactionFormValues, 'autoCompute'>({
    name: 'autoCompute',
  });
  const setValueOptions = useMemo(
    (): { shouldDirty: boolean; shouldValidate: boolean } => ({
      shouldDirty: true,
      shouldValidate: true,
    }),
    [],
  );

  /** Apply recalculated transaction values to React Hook Form. */
  const setCalculatedValues = useCallback(
    (values: TransactionPricingValues): void => {
      setValue('quantity', values.quantity, {
        shouldDirty: true,
        shouldValidate: true,
      });
      setValue('tt', values.tt, setValueOptions);
      setValue('fee', values.fee, setValueOptions);
      setValue('ttc', values.ttc, setValueOptions);
    },
    [setValue, setValueOptions],
  );

  useEffect((): void => {
    const pricing = new TransactionPricing(action, item);
    pricingRef.current = pricing;
    setCalculatedValues(pricing.getValues());
  }, [setCalculatedValues, item, action]);

  /** Toggle automatic transaction pricing. */
  const handleAutoComputeChange = (checked: boolean): void => {
    if (!pricingRef.current) return;
    if (checked) {
      const values = getValues();
      void pricingRef.current
        .update('fee', values.fee, true)
        .then(setCalculatedValues);
    }
  };

  return (
    <div className={styles.fields}>
      <TransactionTypeAndQuantityFields
        action={action}
        isStackable={isStackable}
      />
      {action === 'sell' ? (
        <p>{t('TRANSACTION_MODAL.SELL_DETAILS_NOTICE')}</p>
      ) : null}
      <TransactionInputs
        isStackable={isStackable}
        feeReadOnly={action === 'sell' && autoCompute}
        autoCompute={autoCompute}
        pricingRef={pricingRef}
        setCalculatedValues={setCalculatedValues}
      />
      <CheckboxRHF
        name="autoCompute"
        label={t('TRANSACTION_MODAL.AUTO_COMPUTE')}
        wrapperClassName={styles.autoComputeToggle}
        onCheckedChange={(checked): undefined =>
          void handleAutoComputeChange(checked)
        }
      />
    </div>
  );
}

export default TransactionForm;
