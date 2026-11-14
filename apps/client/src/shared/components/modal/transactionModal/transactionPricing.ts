import { ItemStoreRow } from '@/shared/types';
import type { TransactionAction, TransactionLot } from '@/shared/types/modal';
import { isStackableItem, numericValue } from '@/shared/utils';

export type PricingAction = TransactionAction;
export type TransactionPricingField = 'quantity' | 'tt' | 'fee' | 'ttc';

/** Draft values maintained by the transaction pricing form. */
export type TransactionPricingValues = {
  quantity: number;
  tt: number;
  fee: number;
  ttc: number;
};

/** Own transaction values and apply automatic pricing transitions. */
export class TransactionPricing {
  private autoCompute = true;
  private itemTtValue = 0;
  private isStackable = false;
  private values: TransactionPricingValues;

  constructor(
    private readonly action: PricingAction,
    item: ItemStoreRow | null,
    lot: TransactionLot | null,
  ) {
    this.autoCompute = action !== 'buy';
    this.isStackable = Boolean(item && isStackableItem(item) && !lot);
    this.itemTtValue = item?.tt ?? 0;

    const tt = lot
      ? numericValue(lot.tt_remaining ?? '')
      : item?.tt ?? 0;

    this.values = {
      quantity: 1,
      tt,
      fee: 0,
      ttc: Math.ceil(tt),
    };
  }

  /** Return the current transaction values owned by the pricing session. */
  getValues(): TransactionPricingValues {
    return this.values;
  }

  /** Return whether automatic pricing is enabled for the current transaction. */
  getAutoCompute(): boolean {
    return this.autoCompute;
  }

  /** Enable or disable automatic pricing for subsequent edits. */
  setAutoCompute(value: boolean) {
    this.autoCompute = value;
  }

  /** Normalize a numeric input while preserving decimal values except quantity. */
  private normalizeValue(field: TransactionPricingField, value: number): number {
    return field === 'quantity' ? Math.max(1, Math.floor(value)) : value;
  }

  /** Update one field and asynchronously return the recalculated transaction values. */
  async update(
    field: TransactionPricingField,
    value: number | undefined,
  ): Promise<TransactionPricingValues> {
    if (value === undefined || !this.canUpdate(field, value)) {
      return this.values;
    }

    const normalizedValue = this.normalizeValue(field, value);
    this.values =
      this.action === 'buy'
        ? this.updateBuy(field, normalizedValue)
        : this.updateSell(field, normalizedValue);

    return this.values;
  }

  /** Return whether a field can update the pricing session in its current mode. */
  private canUpdate(
    field: TransactionPricingField,
    value: number | undefined,
  ): boolean {
    return Boolean(
      field &&
        value !== undefined &&
        (this.autoCompute || this.action === 'buy'),
    );
  }

  /** Apply a buy input and keep TTC valid when TT or fee changes. */
  private updateBuy(
    field: TransactionPricingField,
    value: number,
  ): TransactionPricingValues {
    const nextValues =
      field === 'quantity'
        ? {
            ...this.values,
            quantity: value,
            tt: value * this.itemTtValue,
          }
        : { ...this.values, [field]: value };

    return field === 'ttc'
      ? nextValues
      : this.ensureTtcCoversAmount(nextValues);
  }

  /** Apply a sale input while respecting stackability and temporary TTC edits. */
  private updateSell(
    field: TransactionPricingField,
    value: number,
  ): TransactionPricingValues {
    if (field === 'quantity' && !this.isStackable) return this.values;
    if (field === 'tt' && this.isStackable) return this.values;

    const nextValues =
      field === 'quantity'
        ? {
            ...this.values,
            quantity: value,
            tt: value * this.itemTtValue,
          }
        : { ...this.values, [field]: value };

    return field === 'ttc'
      ? nextValues
      : this.ensureTtcCoversAmount(nextValues);
  }

  /** Keep TTC above TT plus fee, recalculating fees when needed. */
  private ensureTtcCoversAmount(
    values: TransactionPricingValues,
  ): TransactionPricingValues {
    const { fee } = values;
    let { ttc } = values;
    let calculatedFee = this.calculateFee(values.tt, fee, ttc);

    while (ttc - calculatedFee - values.tt < 0) {
      ttc += 1;
      calculatedFee =
        this.action === 'buy'
          ? calculatedFee
          : this.feeFromMarkup(ttc - values.tt);
    }

    return { ...values, fee: calculatedFee, ttc };
  }

  /** Calculate the fee according to the transaction mode and current markup. */
  private calculateFee(tt: number, fee: number, ttc: number): number {
    if (this.action === 'buy' || fee !== 0) return fee;
    return this.feeFromMarkup(ttc - tt);
  }

  /** Calculate the fee from the markup above TT. */
  private feeFromMarkup(value: number): number {

    if (value <= 0) return 0.5;

    const fee = (99.5 * value + 995) / (value + 1990);
    const result = Math.min(100, Math.floor(fee * 100) / 100);
    return result;
  }
}
