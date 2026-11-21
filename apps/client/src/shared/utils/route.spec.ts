import { describe, expect, it } from 'vitest';

import { buildAppRoute, parseAppRoute, parseQueryValue } from './route';

const definition = {
  prefix: 'transaction',
  kinds: ['finder', 'material'] as const,
  actions: ['buy', 'sell', 'edit'] as const,
};

describe('app routes', () => {
  it('parses JSON-encoded query values generically', () => {
    expect(
      parseQueryValue<{ item_id: string }>(
        JSON.stringify({ item_id: 'item-1' }),
      ),
    ).toEqual({ item_id: 'item-1' });
  });

  it('returns undefined for absent or malformed query values', () => {
    expect(parseQueryValue(undefined)).toBeUndefined();
    expect(parseQueryValue('{malformed')).toBeUndefined();
  });

  it('parses the shared prefix, kind, id, and action segments', () => {
    expect(parseAppRoute('/transaction/finder/item%2F1/sell', definition)).toEqual({
      prefix: 'transaction',
      kind: 'finder',
      id: 'item/1',
      action: 'sell',
    });
  });

  it('rejects unknown prefixes, kinds, and actions', () => {
    expect(parseAppRoute('/other/finder/item/buy', definition)).toEqual({});
    expect(parseAppRoute('/transaction/unknown/item/buy', definition)).toEqual({
      prefix: 'transaction',
    });
    expect(parseAppRoute('/transaction/finder/item/delete', definition)).toEqual({
      prefix: 'transaction',
      kind: 'finder',
      id: 'item',
    });
  });

  it('builds an encoded absolute route', () => {
    expect(
      buildAppRoute({
        prefix: 'transaction',
        kind: 'finder',
        id: 'item/1',
        action: 'buy',
      }),
    ).toBe('/transaction/finder/item%2F1/buy');
  });
});
