import { describe, expect, it } from 'vitest';
import type { ItemRow } from '@/shared/types/listItem';
import { TransactionPricing } from './transactionPricing';

const item: ItemRow = {
  id: 'material-1',
  name: 'Oil',
  kind: 'material',
  imageUrl: null,
  isRare: false,
  isUntradeable: false,
  tt: 10,
  decay: null,
  stock: 4,
  details: { isStackable: true, type: { id: 'ore', name: 'Ore' } },
};

describe('TransactionPricing', () => {
  it('allows editing the buy fee and keeps TTC above TT plus fee', async () => {
    const pricing = new TransactionPricing('buy', item);

    const afterFee = await pricing.update('fee', 3);

    expect(afterFee).toMatchObject({ tt: 10, fee: 3, ttc: 13 });

    const afterLowerTtc = await pricing.update('ttc', 11);

    expect(afterLowerTtc).toMatchObject({ tt: 10, fee: 3, ttc: 11 });
  });

  it('keeps a temporarily low TTC while editing a sale', async () => {
    const pricing = new TransactionPricing('sell', item);

    const afterFee = await pricing.update('fee', 3);
    const values = await pricing.update('ttc', 11);

    expect(values).toMatchObject({ tt: 10, fee: afterFee.fee, ttc: 11 });
  });

  it('rounds calculated decimal values to two places', async () => {
    const pricing = new TransactionPricing('buy', {
      ...item,
      tt: 10.123,
    });

    const values = await pricing.update('quantity', 3);

    expect(values).toMatchObject({ tt: 30.37, fee: 0, ttc: 31 });
  });
});

describe('transaction pricing invariants', () => {
  it('uses selected equipment TT and keeps an existing instance quantity fixed', async () => {
    const pricing = new TransactionPricing('sell', {
      ...item,
      ttRemaining: '6.25',
      details: { ...item.details, isStackable: false },
    });
    expect(pricing.getValues()).toEqual({
      quantity: 1,
      tt: 6.25,
      fee: 0,
      ttc: 7,
    });
    expect(await pricing.update('quantity', 5)).toEqual(pricing.getValues());
  });

  it('uses automatic auction fees while preserving manually entered fees', async () => {
    const automatic = new TransactionPricing('sell', item);
    const manual = new TransactionPricing('sell', item);
    const autoValues = await automatic.update('quantity', 2, true);
    const manualValues = await manual.update('quantity', 2, false);
    expect(autoValues).toEqual({ quantity: 2, tt: 20, fee: 0.54, ttc: 21 });
    expect(manualValues).toEqual({ quantity: 2, tt: 20, fee: 0, ttc: 20 });
    expect(await manual.update('fee', 3, false)).toEqual({
      quantity: 2,
      tt: 20,
      fee: 3,
      ttc: 23,
    });
  });

  it('scales equipment purchase summaries without altering per-instance payload prices', () => {
    const values = { quantity: 1, tt: 6.25, fee: 0.5, ttc: 8 };
    expect(TransactionPricing.summarize(values, 'buy', false, 3)).toMatchObject(
      { quantity: 3, tt: 18.75, fee: 1.5, ttc: 24 },
    );
    expect(values).toEqual({ quantity: 1, tt: 6.25, fee: 0.5, ttc: 8 });
    expect(
      TransactionPricing.summarize(values, 'sell', false, 3),
    ).toMatchObject({ quantity: 1, tt: 6.25, fee: 0.5, ttc: 8 });
  });
});
