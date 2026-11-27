import { describe, expect, it } from 'vitest';
import type {
  FinderResponse,
  ExcavatorResponse,
  FinderAmplifierResponse,
  UnstackableLotResponse,
} from '@/api/generated/model';
import { miningSessionFormDefaultValues } from './miningSessionFormSchema';
import {
  calculateMiningSession,
  minimumTier,
  selectUsefulFinders,
} from './miningSessionCalculation';
import type { MiningEquipment } from './useMiningEquipment';

/** Build typed catalogue and owned-lot fixtures for session calculation regressions. */
function fixture(limited = true) {
  const finder = {
    id: 'finder',
    name: 'Finder',
    economy: { decay: '0.1' },
    details: { ammoBurn: 10, isLimited: limited },
  } as FinderResponse;
  const excavator = {
    id: 'excavator',
    name: 'Excavator',
    details: { isLimited: limited },
  } as ExcavatorResponse;
  const amplifier = {
    id: 'amp',
    name: 'Amp',
    economy: { decay: '2' },
    details: { isLimited: limited },
  } as FinderAmplifierResponse;
  /** Build one available tool lot with current TT and tier. */
  const lot = (
    id: string,
    item: typeof finder | typeof excavator | typeof amplifier,
    tt: string,
    tier = 0,
  ) =>
    ({
      id,
      userId: 'user',
      type: 'TOOL',
      isDefault: false,
      createdAt: '',
      updatedAt: null,
      item,
      tt,
      tier,
      qty: 1,
      reserved: 0,
      isActive: true,
    }) as UnstackableLotResponse;
  const equipment: MiningEquipment = {
    finders: [finder],
    excavators: [excavator],
    amplifiers: [amplifier],
    enhancers: [],
    enhancerStock: {},
    lots: [
      lot('f1', finder, '0.6', 4),
      lot('f2', finder, '0.6'),
      lot('e1', excavator, '0'),
      lot('a1', amplifier, '183'),
      lot('a2', amplifier, '183'),
    ],
  };
  const values = {
    ...miningSessionFormDefaultValues,
    clicks: 10,
    planet: 'planet',
    finderLotIds: ['f1', 'f2'],
    excavatorLotIds: ['e1'],
  };
  return { equipment, values };
}

describe('mining session calculations', () => {
  it.each([
    ['E', 5, 1],
    ['O', 10, 1],
    ['OE', 15, 2],
  ] as const)(
    'prices ammo and finder decay for %s',
    (searchType, ammo, decay) => {
      const { equipment, values } = fixture(false);
      const estimate = calculateMiningSession(
        { ...values, searchType, finderLotIds: ['f1'] },
        equipment,
      );
      expect(estimate.ammo).toBe(ammo);
      expect(estimate.finderDecay).toBe(decay);
      expect(estimate.finderAmmoByLot.f1).toBe(ammo);
    },
  );

  it('pools TT only from selected finders and uses their lowest tier', () => {
    const { equipment, values } = fixture();
    const estimate = calculateMiningSession(values, equipment);
    expect(estimate.issues).toEqual([]);
    expect(minimumTier(estimate.finderLots)).toBe(0);
    expect(
      calculateMiningSession(
        { ...values, finderLotIds: ['f1'] },
        equipment,
      ).issues.some((issue) => issue.path === 'finderLotIds'),
    ).toBe(true);
  });

  it('preserves the primary finder and trims trailing lots once covered', () => {
    const { equipment } = fixture();
    const [first, second] = equipment.lots;
    const sufficient = { ...first, id: 'sufficient', tt: '1' };
    expect(selectUsefulFinders([first, sufficient, second], 1, true)).toEqual([
      first,
      sufficient,
    ]);
    expect(
      selectUsefulFinders([first, second, { ...first, id: 'third' }], 1, true),
    ).toHaveLength(2);
    expect(selectUsefulFinders([first, second], 1, false)).toEqual([first]);
  });

  it('allocates decay and ammo in selection order even when the second finder could cover the session alone', () => {
    const { equipment, values } = fixture();
    equipment.lots[0].tt = '0.8';
    equipment.lots[1].tt = '1';
    const estimate = calculateMiningSession(values, equipment);
    expect(estimate.finderLots.map((lot) => lot.id)).toEqual(['f1', 'f2']);
    expect(estimate.finderDecayByLot.f1).toBe(0.8);
    expect(estimate.finderDecayByLot.f2).toBeCloseTo(0.2);
    expect(estimate.finderAmmoByLot.f1).toBeCloseTo(4);
    expect(estimate.finderAmmoByLot.f2).toBeCloseTo(1);
  });

  it('estimates TTC using markup only on L tools and leaves ammunition at TT', () => {
    const { equipment, values } = fixture();
    equipment.finders[0].economy.avgMuPercent = '150';
    equipment.amplifiers[0].economy.avgMuPercent = '125';
    const estimate = calculateMiningSession(
      { ...values, amplifierItemId: 'amp' },
      equipment,
    );
    expect(estimate.total).toBe(26);
    expect(estimate.totalTtc).toBe(31.5);
    equipment.finders[0].details.isLimited = false;
    equipment.amplifiers[0].details.isLimited = false;
    const unlimited = calculateMiningSession(
      { ...values, amplifierItemId: 'amp' },
      equipment,
    );
    expect(unlimited.totalTtc).toBe(unlimited.total);
  });

  it('defaults missing L markup to TT and never charges a flat markup on unused amplifiers', () => {
    const { equipment, values } = fixture();
    equipment.amplifiers[0].economy.avgMuPlus = '3';
    const estimate = calculateMiningSession(
      { ...values, amplifierItemId: 'amp' },
      equipment,
    );
    expect(estimate.totalTtc).toBe(29);
    expect(calculateMiningSession(values, equipment).totalTtc).toBe(6);
  });

  it('discards each amplifier residue before summing capacities', () => {
    const { equipment, values } = fixture();
    expect(
      calculateMiningSession({ ...values, amplifierItemId: 'amp' }, equipment)
        .amplifierClicks,
    ).toBe(182);
    expect(
      calculateMiningSession(
        { ...values, amplifierItemId: 'amp', searchType: 'OE' },
        equipment,
      ).amplifierClicks,
    ).toBe(90);
  });

  it('allows repairable unlimited tools despite their low current TT', () => {
    const { equipment, values } = fixture(false);
    const estimate = calculateMiningSession(
      {
        ...values,
        clicks: 10000,
        finderLotIds: ['f1'],
        amplifierItemId: 'amp',
      },
      equipment,
    );
    expect(estimate.issues).toEqual([]);
    expect(estimate.amplifierClicks).toBe(Infinity);
  });
});
