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

/** Own transaction values and apply all auction-pricing transitions. */
export class TransactionPricing {
  private isAuction = true;
  private itemTtValue = 0;
  private isStackable = false;
  private values: TransactionPricingValues;

  constructor(
    private readonly action: PricingAction,
    item: ItemStoreRow | null,
    lot: TransactionLot | null,
  ) {
    this.isAuction = action !== 'buy';
    this.isStackable = Boolean(item && isStackableItem(item) && !lot);
    this.itemTtValue = numericValue(item?.tt ?? '');

    const tt = lot
      ? numericValue(lot.tt_remaining ?? '')
      : numericValue(item?.tt ?? '');

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

  /** Return whether auction pricing is enabled for the current transaction. */
  getIsAuction(): boolean {
    return this.isAuction;
  }

  /** Enable or disable auction fee recalculation for subsequent edits. */
  setAuction(value: boolean) {
    this.isAuction = value;
  }

  normalizeValue(field: TransactionPricingField, value: number) {
    return field === 'quantity' ? Math.max(1, Math.floor(value)) : value;
  }

  /** Update one field and asynchronously return the recalculated transaction values. */
  async update(
    field: TransactionPricingField,
    value: number | undefined,
  ): Promise<TransactionPricingValues> {
    if (
      value === undefined ||
      !field ||
      (!this.isAuction && this.action !== 'buy')
    ) {
      return this.values;
    }

    const normalizedValue = this.normalizeValue(field, value);

    if (this.action === 'buy') {
      if (field === 'quantity') {
        this.values = {
          ...this.values,
          [field]: normalizedValue,
          tt: normalizedValue * this.itemTtValue,
        };
      } else {
        this.values = { ...this.values, [field]: normalizedValue };
      }
      const result = this.getValuesFromUpdate(this.values);
      this.values = { ...this.values, ...result };
      return this.values;
    } else {
      let result: Omit<TransactionPricingValues, 'quantity'> = this.values;

      switch (field) {
        case 'quantity':
          {
            if (!this.isStackable) {
              return this.values;
            }
            const tt = normalizedValue * this.itemTtValue;
            result = this.getValuesFromUpdate({
              ...this.getValues(),
              tt,
            });
          }
          break;
        case 'tt':
          if (this.isStackable) return this.values;

          result = this.getValuesFromUpdate({
            ...this.getValues(),
            tt: value,
          });
          break;
        case 'fee':
          result = this.getValuesFromUpdate({
            ...this.getValues(),
            fee: value,
          });
          break;
        case 'ttc':
          result = this.getValuesFromUpdate({
            ...this.getValues(),
            ttc: value,
          });
          break;
        default:
          result = this.values;
          break;
      }

      this.values = {
        ...this.values,
        ...(field === 'quantity' ? { quantity: normalizedValue } : {}),
        ...result,
      };

      return this.values;
    }
  }

  /** Recalculate fee and TTC while keeping the sale financially valid. */
  getValuesFromUpdate({
    tt,
    fee,
    ttc,
  }: Omit<TransactionPricingValues, 'quantity'>) {
    let feeInternal = fee === 0 ? this.feeFromMarkup(ttc - tt) : fee;

    while (ttc - feeInternal - tt < 0) {
      ttc += 1;
      feeInternal = this.feeFromMarkup(ttc - tt);
    }

    const result = { tt, fee: feeInternal, ttc };
    return result;
  }

  /** Calculate the auction fee from the markup above TT. */
  feeFromMarkup(value: number): number {
    if (this.action === 'buy' || !this.isAuction) return this.values.fee;

    if (value <= 0) return 0.5;

    const fee = (99.5 * value + 995) / (value + 1990);
    const result = Math.min(100, Math.floor(fee * 100) / 100);
    return result;
  }
}
