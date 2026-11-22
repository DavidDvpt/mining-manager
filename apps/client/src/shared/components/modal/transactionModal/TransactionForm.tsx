import { JSX, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useFormContext } from 'react-hook-form';
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
  const { setValue } = useFormContext<TransactionFormValues>();
  const { t } = useTranslations();
  const [autoCompute, setAutoCompute] = useState(action === 'sell');
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
    setAutoCompute(checked);
  };

  return (
    <div className={styles.fields}>
      {action === 'buy' && (
        <TransactionTypeAndQuantityFields
          action="buy"
          isStackable={isStackable}
        />
      )}
      <TransactionInputs
        isStackable={isStackable}
        feeReadOnly={action === 'sell' && autoCompute}
        autoCompute={autoCompute}
        pricingRef={pricingRef}
        setCalculatedValues={setCalculatedValues}
      />
      <CheckboxRHF
        name="autoCompute"
        checked={autoCompute}
        bindToForm={false}
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
