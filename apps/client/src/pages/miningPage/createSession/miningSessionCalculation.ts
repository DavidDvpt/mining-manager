import type { TranslationKey } from '@/i18n/types';
import type { MiningSessionFormValues } from '@/shared/types/mining';
import type {
  EconomyResponse,
  UnstackableLotResponse,
} from '@/api/generated/model';
import {
  getAmplifierClicks,
  getMiningAmmoMultiplier,
  getMiningDecayMultiplier,
  toPositiveNumber,
} from '../utils';
import type { MiningEquipment } from './useMiningEquipment';

/** Return the minimum tier among selected owned tools; empty selection has no sockets. */
export function minimumTier(lots: UnstackableLotResponse[]): number {
  return lots.length ? Math.min(...lots.map((lot) => lot.tier ?? 0)) : 0;
}

/** Retain only useful user-selected finders; a repairable UL or sufficient L stands alone. */
export function selectUsefulFinders(
  lots: UnstackableLotResponse[],
  requiredDecay: number,
  limited: boolean,
): UnstackableLotResponse[] {
  if (!limited) return lots.slice(0, 1);
  const tolerance = Number.EPSILON * Math.max(1, requiredDecay) * 4;
  const usable = lots.filter((lot) => toPositiveNumber(lot.tt) > 0);
  const sufficient = usable.find(
    (lot) => toPositiveNumber(lot.tt) + tolerance >= requiredDecay,
  );
  if (sufficient) return [sufficient];
  let total = usable.reduce((sum, lot) => sum + toPositiveNumber(lot.tt), 0);
  const retained = [...usable];
  for (let index = retained.length - 1; index >= 0; index--) {
    const tt = toPositiveNumber(retained[index].tt);
    if (total - tt + tolerance >= requiredDecay) {
      retained.splice(index, 1);
      total -= tt;
    }
  }
  return retained.sort(
    (a, b) =>
      toPositiveNumber(a.tt) - toPositiveNumber(b.tt) ||
      a.id.localeCompare(b.id),
  );
}

/** Apply catalogue markup to an L tool's consumed TT; UL tools and unpriced L tools stay at 100%. */
export function miningCostTtc(
  value: number,
  limited: boolean,
  economy?: EconomyResponse,
): number {
  if (!limited || value === 0 || !economy) return value;
  if (economy.avgMuPercent != null)
    return (value * Number(economy.avgMuPercent)) / 100;
  if (economy.avgMuPlus != null) return value + Number(economy.avgMuPlus);
  return value;
}

/** Estimate TT/TTC costs using L catalogue markup, allocate finder decay, and validate selections. */
export function calculateMiningSession(
  values: MiningSessionFormValues,
  equipment: MiningEquipment,
) {
  const { lots, finders, excavators, amplifiers, enhancers, enhancerStock } =
    equipment;
  const finder = finders.find((item) => item.id === values.finderItemId);
  const finderLots = lots
    .filter(
      (lot) =>
        values.finderLotIds.includes(lot.id) &&
        lot.item.id === values.finderItemId,
    )
    .sort(
      (a, b) =>
        toPositiveNumber(a.tt) - toPositiveNumber(b.tt) ||
        a.id.localeCompare(b.id),
    );
  const excavatorLots = lots.filter(
    (lot) =>
      values.excavatorLotIds.includes(lot.id) &&
      excavators.some((item) => item.id === lot.item.id),
  );
  const amplifier = amplifiers.find(
    (item) => item.id === values.amplifierItemId,
  );
  const amplifierLots = lots.filter((lot) => lot.item.id === amplifier?.id);
  const count = getMiningDecayMultiplier(values.searchType);
  const finderDecay =
    values.clicks * count * toPositiveNumber(finder?.economy.decay);
  const ammo =
    values.clicks *
    (finder?.details.ammoBurn ?? 0) *
    getMiningAmmoMultiplier(values.searchType) *
    0.05;
  const finderTt = finderLots.reduce(
    (sum, lot) => sum + toPositiveNumber(lot.tt),
    0,
  );
  const amplifierClicks =
    amplifier?.details.isLimited === false
      ? Infinity
      : amplifierLots.reduce(
          (sum, lot) =>
            sum +
            getAmplifierClicks(
              lot.tt,
              amplifier?.economy.decay ?? null,
              1,
              values.searchType,
            ),
          0,
        );
  const amplifierCost = amplifier
    ? values.clicks * count * toPositiveNumber(amplifier.economy.decay)
    : 0;
  const issues: { path: string; message: TranslationKey }[] = [];
  if (
    !finder ||
    finderLots.length !== values.finderLotIds.length ||
    !finderLots.length
  )
    issues.push({
      path: 'finderLotIds',
      message: 'MINING.SETUP.INVALID_FINDERS',
    });
  if (
    finder &&
    (finder.details.ammoBurn === null ||
      toPositiveNumber(finder.economy.decay) === 0)
  )
    issues.push({
      path: 'finderItemId',
      message: 'MINING.SETUP.INCOMPLETE_FINDER',
    });
  if (
    finder?.details.isLimited &&
    (finderLots.some((lot) => lot.tt === null) ||
      finderTt + Number.EPSILON * Math.max(1, finderTt, finderDecay) * 4 <
        finderDecay)
  )
    issues.push({
      path: 'finderLotIds',
      message: 'MINING.SETUP.FINDER_CAPACITY',
    });
  if (
    excavatorLots.length !== values.excavatorLotIds.length ||
    !excavatorLots.length
  )
    issues.push({
      path: 'excavatorLotIds',
      message: 'MINING.SETUP.INVALID_EXCAVATORS',
    });
  if (
    values.amplifierItemId &&
    (!amplifier ||
      !amplifierLots.length ||
      !toPositiveNumber(amplifier.economy.decay) ||
      amplifierClicks < values.clicks)
  )
    issues.push({
      path: 'amplifierItemId',
      message: 'MINING.SETUP.AMP_CAPACITY',
    });
  for (const [field, selected, tool] of [
    ['enhancers', finderLots, 'FINDER'],
    ['excavatorEnhancers', excavatorLots, 'EXCAVATOR'],
  ] as const) {
    for (const [socket, id] of Object.entries(values[field])) {
      if (!id) continue;
      const enhancer = enhancers.find((item) => item.id === id);
      if (
        !enhancer ||
        enhancer.details.tool !== tool ||
        socket !== `s${enhancer.details.socket}` ||
        enhancer.details.socket > minimumTier(selected) ||
        (enhancerStock[id] ?? 0) < 1
      )
        issues.push({
          path: `${field}.${socket}`,
          message: 'MINING.SETUP.INVALID_ENHANCER',
        });
    }
  }
  let remainingDecay = finderDecay;
  const finderDecayByLot = Object.fromEntries(
    finderLots.map((lot) => {
      const decay = Math.min(
        remainingDecay,
        finder?.details.isLimited ? toPositiveNumber(lot.tt) : remainingDecay,
      );
      remainingDecay = Math.max(0, remainingDecay - decay);
      return [lot.id, decay];
    }),
  );
  const finderTtc = miningCostTtc(
    finderDecay,
    finder?.details.isLimited ?? false,
    finder?.economy,
  );
  let remainingAmpClicks = values.clicks;
  const amplifierTtc = amplifierLots.reduce((total, lot) => {
    if (!amplifier || remainingAmpClicks <= 0) return total;
    const capacity = amplifier.details.isLimited
      ? getAmplifierClicks(
          lot.tt,
          amplifier.economy.decay,
          1,
          values.searchType,
        )
      : remainingAmpClicks;
    const usedClicks = Math.min(remainingAmpClicks, capacity);
    remainingAmpClicks -= usedClicks;
    const consumed =
      usedClicks * count * toPositiveNumber(amplifier.economy.decay);
    return (
      total +
      miningCostTtc(consumed, amplifier.details.isLimited, amplifier.economy)
    );
  }, 0);
  return {
    finder,
    finderLots,
    excavatorLots,
    amplifier,
    amplifierLots,
    finderDecay,
    finderDecayByLot,
    finderTt,
    ammo,
    amplifierClicks,
    amplifierCost,
    total: ammo + finderDecay + amplifierCost,
    totalTtc: ammo + finderTtc + amplifierTtc,
    finderTtc,
    amplifierTtc,
    issues,
  };
}
