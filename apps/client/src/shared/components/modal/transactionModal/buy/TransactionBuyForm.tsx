import { JSX, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useFormContext } from 'react-hook-form';
import { CheckboxRHF } from '@/shared/components/form/CheckboxRHF';
import type { TransactionFormValues } from '@/shared/types/modal';
import {
  TransactionPricing,
  type TransactionPricingValues,
} from '../transactionPricing';
import styles from '../transaction-modal.module.scss';
import type { ItemRow } from '@/shared/types';
import { useTranslations } from '@/i18n/useTranslations';
import { TransactionInputs } from '../TransactionInputs';
import { TransactionTypeAndQuantityFields } from '../TransactionTypeAndQuantityFields';

type TransactionBuyFormProps = {
  isStackable: boolean;
  item: ItemRow | null;
};

/** Render buy inputs and synchronize edits with buy-specific pricing rules. */
export function TransactionBuyForm({
  isStackable,
  item,
}: TransactionBuyFormProps): JSX.Element {
  const pricingRef = useRef<TransactionPricing | null>(null);
  const { setValue } = useFormContext<TransactionFormValues>();
  const { t } = useTranslations();
  const [autoCompute, setAutoCompute] = useState(false);

  const setValueOptions = useMemo((): {
    shouldDirty: boolean;
    shouldValidate: boolean;
  } => {
    return { shouldDirty: true, shouldValidate: true };
  }, []);

  /** Apply recalculated buy values to React Hook Form. */
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
    const pricing = new TransactionPricing('buy', item, null);
    pricingRef.current = pricing;
    setCalculatedValues(pricing.getValues());
  }, [setCalculatedValues, item, setValue]);

  /** Toggle automatic buy pricing and synchronize the pricing session. */
  const handleAutoComputeChange = (checked: boolean): void => {
    if (!pricingRef.current) return;
    setAutoCompute(checked);
  };

  return (
    <div className={styles.fields}>
      <TransactionTypeAndQuantityFields action="buy" isStackable={isStackable} />
      <TransactionInputs
        isStackable={isStackable}
        feeReadOnly={false}
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

export default TransactionBuyForm;
