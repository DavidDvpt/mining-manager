import { useMemo, type JSX, type RefObject } from 'react';
import { useFormContext } from 'react-hook-form';
import { InputRHF } from '@/shared/components/form/InputRHF';
import { parseInputValue } from '@/shared/utils';
import { useTranslations } from '@/i18n/useTranslations';
import type { TransactionFormValues } from '@/shared/types/modal';
import {
  TransactionPricing,
  type TransactionPricingField,
  type TransactionPricingValues,
} from './transactionPricing';
import styles from './transaction-modal.module.scss';

type TransactionInputsProps = {
  isStackable: boolean;
  feeReadOnly: boolean;
  autoCompute: boolean;
  pricingRef: RefObject<TransactionPricing | null>;
  setCalculatedValues: (values: TransactionPricingValues) => void;
};

/** Render the numeric inputs shared by buy and sell transaction forms. */
export function TransactionInputs({
  isStackable,
  feeReadOnly,
  autoCompute,
  pricingRef,
  setCalculatedValues,
}: TransactionInputsProps): JSX.Element {
  const { setValue } = useFormContext<TransactionFormValues>();
  const { t } = useTranslations();
  const setValueOptions = useMemo((): {
    shouldDirty: boolean;
    shouldValidate: boolean;
  } => {
    return { shouldDirty: true, shouldValidate: true };
  }, []);

  /** Keep React Hook Form synchronized before recalculating dependent values. */
  const handleChange = async (
    field: TransactionPricingField,
    value: string,
  ): Promise<void> => {
    const parsedValue = parseInputValue(value);
    setValue(field, parsedValue as never, setValueOptions);

    if (!pricingRef.current || value === undefined) return;
    setCalculatedValues(
      await pricingRef.current.update(field, parsedValue, autoCompute),
    );
  };

  return (
    <div className={styles.transactionInputs}>
      <InputRHF
        name="quantity"
        label={t('TRANSACTION_MODAL.QUANTITY')}
        type="number"
        min={1}
        step={1}
        readOnly={!isStackable}
        autoFocus={isStackable}
        onChange={(event): Promise<void> =>
          handleChange('quantity', event.target.value)
        }
      />
      <InputRHF
        name="tt"
        label="TT"
        type="number"
        min={0}
        step="0.01"
        readOnly={isStackable}
        autoFocus={!isStackable}
        onChange={(event): Promise<void> =>
          handleChange('tt', event.target.value)
        }
      />
      <InputRHF
        name="fee"
        label="Fee"
        type="number"
        min={0}
        step="0.01"
        readOnly={feeReadOnly}
        onChange={(event): Promise<void> =>
          handleChange('fee', event.target.value)
        }
      />
      <InputRHF
        name="ttc"
        label="TTC"
        type="number"
        min={0}
        step={1}
        onChange={(event): Promise<void> =>
          handleChange('ttc', event.target.value)
        }
      />
    </div>
  );
}

export default TransactionInputs;
