import { ItemStoreRow } from '@/shared/types';
import type { TransactionAction, TransactionLot } from '@/shared/types/modal';
import { isLimitedItem, isStackableItem, numericValue } from '@/shared/utils';

export type PricingAction = TransactionAction;
export type TransactionPricingField = 'quantity' | 'tt' | 'fee' | 'ttc';

export type PricingValues = {
  quantity: number;
  fee: number;
  ttc: number;
};

/** Draft values maintained by the transaction pricing form. */
export type TransactionPricingValues = {
  quantity: number;
  tt: number;
  fee: number;
  ttc: number;
};

/** Apply recalculated pricing values while preserving the draft TT value. */
export function applyPricingValues(
  previousValues: TransactionPricingValues,
  pricingValues: PricingValues,
  stackable: boolean,
): TransactionPricingValues {
  return {
    ...previousValues,
    quantity: stackable ? pricingValues.quantity : 1,
    fee: pricingValues.fee,
    ttc: pricingValues.ttc,
  };
}

/** Recalculate auction values and apply them to the transaction draft. */
export function calculateTransactionValues(
  action: PricingAction,
  field: TransactionPricingField,
  nextValue: number,
  currentValues: TransactionPricingValues,
): TransactionPricingValues {
  const stackable = currentValues.isStackable;
  const nextQuantity =
    field === 'quantity' ? nextValue : (currentValues.quantity ?? 0);
  const nextTt = field === 'tt' ? nextValue : (currentValues.tt ?? 0);
  const unitPrice = stackable ? currentValues.tt : nextTt;
  const currentFee = currentValues.fee ?? 0;
  const currentTtc = currentValues.ttc ?? 0;
  const pricingValues =
    field === 'quantity' || field === 'tt'
      ? computeQuantityPricing(
          action,
          stackable ? nextQuantity : 1,
          unitPrice,
          currentFee,
          currentTtc,
        )
      : field === 'fee'
        ? computeFeePricing(action, nextQuantity, unitPrice, currentTtc)
        : computeTtcPricing(action, nextQuantity, unitPrice, nextValue);

  return applyPricingValues(currentValues, pricingValues, stackable);
}

/** Own transaction values and apply all auction-pricing transitions. */
export class TransactionPricing {
  private isAuction = true;
  private isLimited = false;
  private itemTtValue = 0;
  private isStackable = false;
  private values: TransactionPricingValues;

  constructor(
    private readonly action: PricingAction,
    item: ItemStoreRow | null,
    lot: TransactionLot | null,
  ) {
    if (item && lot) throw new Error();

    this.isStackable = Boolean(item && isStackableItem(item) && !lot);
    this.isLimited = item ? isLimitedItem(item) : false;
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

  setAuction(value: boolean) {
    this.isAuction = value;
  }

  /** Update one field and asynchronously return the recalculated transaction values. */
  async update(
    field: TransactionPricingField,
    value: number | undefined,
  ): Promise<TransactionPricingValues> {
    if (value === undefined || !field || !this.isAuction) return this.values;

    const normalizedValue =
      field === 'quantity' ? Math.max(1, Math.floor(value)) : value;

    if (this.action === 'buy') {
      this.values = { ...this.values, [field]: normalizedValue };
      return this.values;
    } else {
      let result: Omit<TransactionPricingValues, 'quantity'> = this.values;
      switch (field) {
        case 'quantity':
          {
            if (!this.isStackable) return this.values;
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

      this.values = { ...this.values, ...result };

      return this.values;
    }
  }

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

    return { tt, fee: feeInternal, ttc };
  }

  /** Calculate the auction fee from the markup above TT. */
  feeFromMarkup(value: number): number {
    if (value <= 0) return 0.5;
    const fee = (99.5 * value + 995) / (value + 1990);
    return Math.min(100, Math.floor(fee * 100) / 100);
  }
}
