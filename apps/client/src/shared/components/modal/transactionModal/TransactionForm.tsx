import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useFormContext } from 'react-hook-form';
import { CheckboxRHF } from '@/shared/components/form/CheckboxRHF';
import type {
  TransactionFormValues,
  TransactionLot,
} from '@/shared/types/modal';
import {
  TransactionPricing,
  type TransactionPricingValues,
} from './transactionPricing';
import styles from './transaction-modal.module.scss';
import { ItemRow } from '@/shared/types';
import { useTranslations } from '@/i18n/useTranslations';
import { Label } from '@/components/ui/label/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';
import { TransactionInputs } from './TransactionInputs';
import { TransactionTypeAndQuantityFields } from './TransactionTypeAndQuantityFields';

type TransactionFormProps = {
  action: 'buy' | 'sell';
  isStackable: boolean;
  item: ItemRow | null;
  lot: TransactionLot | null;
  lots: TransactionLot[];
  selectedLotId: string | null;
  onLotChange: (lotId: string) => void;
};

/** Format a lot's TT with exactly two decimal places for consistent instance labels. */
function formatLotTt(tt: string | null): string {
  const numericTt = Number(tt);
  return Number.isFinite(numericTt) ? numericTt.toFixed(2) : '—';
}

/** Render transaction inputs and synchronize every edit with transaction pricing. */
export function TransactionForm({
  action,
  isStackable,
  item,
  lot,
  lots,
  selectedLotId,
  onLotChange,
}: TransactionFormProps): import('react').JSX.Element {
  const pricingRef = useRef<TransactionPricing | null>(null);
  const { setValue } = useFormContext<TransactionFormValues>();
  const { t } = useTranslations();
  const [autoCompute, setAutoCompute] = useState(action === 'sell');

  const setValueOptions = useMemo((): {
    shouldDirty: boolean;
    shouldValidate: boolean;
  } => {
    return { shouldDirty: true, shouldValidate: true };
  }, []);

  /** Apply recalculated values to React Hook Form. */
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
    const pricing = new TransactionPricing(action, item, lot);
    pricingRef.current = pricing;
    setAutoCompute(action === 'sell');
    setCalculatedValues(pricing.getValues());
  }, [action, setCalculatedValues, item, lot, setValue]);

  /** Toggle automatic pricing and synchronize recalculated values. */
  const handleAutoComputeChange = (checked: boolean): void => {
    if (!pricingRef.current) return;
    setAutoCompute(checked);
  };

  return (
    <div className={styles.fields}>
      {action === 'sell' && lots.length > 1 ? (
        <div className={styles.lotSelector}>
          <Label htmlFor="transaction-lot">
            {t('TRANSACTION_MODAL.INSTANCE')}
          </Label>
          <Select
            value={selectedLotId ?? lots[0]?.id ?? ''}
            onValueChange={onLotChange}
          >
            <SelectTrigger id="transaction-lot">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {lots.map((availableLot): import('react').JSX.Element => (
                <SelectItem key={availableLot.id} value={availableLot.id}>
                  <span className={styles.lotOptionLabel}>
                    <span>
                      {availableLot.item.name} T{availableLot.tier ?? 0}
                    </span>
                    <span>TT {formatLotTt(availableLot.tt)}</span>
                  </span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
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
        checked={autoCompute}
        bindToForm={false}
        label={t('TRANSACTION_MODAL.AUTO_COMPUTE')}
        wrapperClassName={styles.autoComputeToggle}
        onCheckedChange={(checked): undefined =>
          void handleAutoComputeChange(checked)
        }
      />
      <TransactionTypeAndQuantityFields
        action={action}
        isStackable={isStackable}
      />
    </div>
  );
}

export default TransactionForm;
