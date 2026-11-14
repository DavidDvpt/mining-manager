import { describe, expect, it } from 'vitest';
import type { ItemStoreRow } from '@/shared/types/listItem';
import { TransactionPricing } from './transactionPricing';

const item: ItemStoreRow = {
  id: 'material-1',
  name: 'Oil',
  kind: 'material',
  imageUrl: null,
  isRare: false,
  isUntradeable: false,
  tt: '10.00',
  decay: null,
  stock: 4,
  details: {},
};

describe('TransactionPricing', () => {
  it('starts buy transactions without auction pricing and can synchronize it', () => {
    const pricing = new TransactionPricing('buy', item, null);

    expect(pricing.getIsAuction()).toBe(false);

    pricing.setAuction(true);

    expect(pricing.getIsAuction()).toBe(true);
  });

  it('allows editing the buy fee and keeps TTC above TT plus fee', async () => {
    const pricing = new TransactionPricing('buy', item, null);

    const afterFee = await pricing.update('fee', 3);

    expect(afterFee).toMatchObject({ tt: 10, fee: 3, ttc: 13 });

    const afterLowerTtc = await pricing.update('ttc', 11);

    expect(afterLowerTtc).toMatchObject({ tt: 10, fee: 3, ttc: 11 });
  });

  it('keeps a temporarily low TTC while editing a sale', async () => {
    const pricing = new TransactionPricing('sell', item, null);

    const afterFee = await pricing.update('fee', 3);
    const values = await pricing.update('ttc', 11);

    expect(values).toMatchObject({ tt: 10, fee: afterFee.fee, ttc: 11 });
  });
});
