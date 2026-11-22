import type { TransactionAction, TransactionItem } from '@/shared/types/modal';
import { numericValue } from '@/shared/utils';

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
  private itemTtValue = 0;
  private isStackable = false;
  private values: TransactionPricingValues;

  constructor(
    private readonly action: PricingAction,
    item: TransactionItem | null,
  ) {
    this.isStackable = Boolean(item?.details.isStackable);
    this.itemTtValue = item?.tt ?? 0;

    const tt =
      item?.ttRemaining !== undefined && item.ttRemaining !== null
        ? numericValue(item.ttRemaining)
        : (item?.tt ?? 0);

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

  /** Normalize a numeric input while preserving decimal values except quantity. */
  private normalizeValue(
    field: TransactionPricingField,
    value: number,
  ): number {
    if (field === 'quantity') return Math.max(1, Math.floor(value));
    return Math.round(value * 100) / 100;
  }

  /** Update one field and asynchronously return the recalculated transaction values. */
  async update(
    field: TransactionPricingField,
    value: number | undefined,
    autoCompute = true,
  ): Promise<TransactionPricingValues> {
    if (value === undefined || !field) {
      return this.values;
    }

    const normalizedValue = this.normalizeValue(field, value);
    const nextValues =
      this.action === 'buy'
        ? this.updateBuy(field, normalizedValue)
        : this.updateSell(field, normalizedValue, autoCompute);
    this.values = this.roundPricingValues(nextValues);

    return this.values;
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
      : this.ensureTtcCoversAmount(nextValues, true);
  }

  /** Apply a sale input while respecting stackability and temporary TTC edits. */
  private updateSell(
    field: TransactionPricingField,
    value: number,
    autoCompute: boolean,
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
      : this.ensureTtcCoversAmount(nextValues, autoCompute);
  }

  /** Keep TTC above TT plus fee, recalculating fees when needed. */
  private ensureTtcCoversAmount(
    values: TransactionPricingValues,
    autoCompute: boolean,
  ): TransactionPricingValues {
    const { fee } = values;
    let { ttc } = values;
    let calculatedFee = this.calculateFee(values.tt, fee, ttc, autoCompute);

    while (ttc - calculatedFee - values.tt < 0) {
      ttc += 1;
      calculatedFee =
        this.action === 'buy' || !autoCompute
          ? calculatedFee
          : this.feeFromMarkup(ttc - values.tt);
    }

    return {
      ...values,
      fee: this.roundToTwoDecimals(calculatedFee),
      ttc: this.roundToTwoDecimals(ttc),
      tt: this.roundToTwoDecimals(values.tt),
    };
  }

  /** Calculate the fee according to the transaction mode and current markup. */
  private calculateFee(
    tt: number,
    fee: number,
    ttc: number,
    autoCompute: boolean,
  ): number {
    if (this.action === 'buy' || !autoCompute || fee !== 0) return fee;
    return this.feeFromMarkup(ttc - tt);
  }

  /** Calculate the fee from the markup above TT. */
  private feeFromMarkup(value: number): number {
    if (value <= 0) return 0.5;

    const fee = (99.5 * value + 995) / (value + 1990);
    const result = Math.min(100, Math.floor(fee * 100) / 100);
    return this.roundToTwoDecimals(result);
  }

  /** Round calculated monetary values to the two decimals supported by the form. */
  private roundToTwoDecimals(value: number): number {
    return Math.round((value + Number.EPSILON) * 100) / 100;
  }

  /** Round every decimal pricing field while leaving quantity as an integer. */
  private roundPricingValues(
    values: TransactionPricingValues,
  ): TransactionPricingValues {
    return {
      quantity: Math.max(1, Math.floor(values.quantity)),
      tt: this.roundToTwoDecimals(values.tt),
      fee: this.roundToTwoDecimals(values.fee),
      ttc: this.roundToTwoDecimals(values.ttc),
    };
  }
}
