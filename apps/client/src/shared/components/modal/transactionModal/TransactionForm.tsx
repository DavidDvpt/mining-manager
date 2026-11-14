import { useCallback, useEffect, useMemo, useRef } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';
import { CheckboxRHF } from '@/shared/components/form/CheckboxRHF';
import { InputRHF } from '@/shared/components/form/InputRHF';
import { parseInputValue, type EditableNumber } from '@/shared/utils';
import type {
  TransactionFormValues,
  TransactionLot,
} from '@/shared/types/modal';
import {
  TransactionPricing,
  type TransactionPricingField,
  type TransactionPricingValues,
} from './transactionPricing';
import styles from './transaction-modal.module.scss';
import { ItemStoreRow } from '@/shared/types';
import { useTranslations } from '@/i18n/useTranslations';
import { Label } from '@/components/ui/label/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';

type TransactionFormProps = {
  action: 'buy' | 'sell';
  isStackable: boolean;
  item: ItemStoreRow | null;
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
}: TransactionFormProps) {
  const pricingRef = useRef<TransactionPricing | null>(null);
  const { setValue } = useFormContext<TransactionFormValues>();
  const { t } = useTranslations();
  const autoCompute = useWatch({
    name: 'autoCompute',
    defaultValue: true,
  });

  const setValueOptions = useMemo(() => {
    return { shouldDirty: true, shouldValidate: true };
  }, []);

  /** Apply recalculated values to React Hook Form. */
  const setCalculatedValues = useCallback(
    (values: TransactionPricingValues) => {
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

  useEffect(() => {
    const pricing = new TransactionPricing(action, item, lot);
    pricingRef.current = pricing;
    setCalculatedValues(pricing.getValues());
    setValue('autoCompute', pricing.getAutoCompute(), { shouldValidate: true });
  }, [action, setCalculatedValues, item, lot, setValue]);

  /** Update one pricing field from a numeric input event. */
  const updateField = async (
    field: TransactionPricingField,
    value: EditableNumber,
  ) => {
    if (!pricingRef.current || value === undefined) return;
    setCalculatedValues(await pricingRef.current.update(field, value));
  };

  /** Keep React Hook Form synchronized before recalculating dependent values. */
  const handleChange = (key: TransactionPricingField, value: string) => {
    const parsedValue = parseInputValue(value);
    // Keep the field empty while the user replaces a value; the schema will
    // prevent submission until a valid numeric value is entered again.
    setValue(key, parsedValue as never, setValueOptions);
    void updateField(key, parsedValue);
  };

  /** Toggle automatic pricing and synchronize recalculated values. */
  const handleAutoComputeChange = (checked: boolean) => {
    if (!pricingRef.current) return;
    pricingRef.current.setAutoCompute(checked);
    setValue(
      'autoCompute',
      pricingRef.current.getAutoCompute(),
      setValueOptions,
    );
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
              {lots.map((availableLot) => (
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
      <InputRHF
        name="quantity"
        label={t('TRANSACTION_MODAL.QUANTITY')}
        type="number"
        min={1}
        step={1}
        readOnly={!isStackable}
        autoFocus={isStackable}
        onChange={(event) => handleChange('quantity', event.target.value)}
      />
      <InputRHF
        name="tt"
        label="TT"
        type="number"
        min={0}
        step="0.01"
        readOnly={isStackable}
        autoFocus={!isStackable}
        onChange={(event) => handleChange('tt', event.target.value)}
      />
      <InputRHF
        name="fee"
        label="Fee"
        type="number"
        min={0}
        step="0.01"
        readOnly={action === 'sell' && autoCompute}
        onChange={(event) => handleChange('fee', event.target.value)}
      />
      <InputRHF
        name="ttc"
        label="TTC"
        type="number"
        min={0}
        step={1}
        onChange={(event) => handleChange('ttc', event.target.value)}
      />
      <CheckboxRHF
        name="autoCompute"
        label={t('TRANSACTION_MODAL.AUTO_COMPUTE')}
        wrapperClassName={styles.autoComputeToggle}
        onCheckedChange={(checked) => void handleAutoComputeChange(checked)}
      />
    </div>
  );
}

export default TransactionForm;
