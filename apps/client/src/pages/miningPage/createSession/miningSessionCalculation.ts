import type { TranslationKey } from '@/i18n/types';
import type { MiningSessionFormValues } from '@/shared/types/mining';
import { numericValue, parseNumber } from '@/shared/utils';
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

/** Keep the selected prefix needed to cover the decay budget, with one finder for UL. */
export function selectUsefulFinders(
  lots: UnstackableLotResponse[],
  requiredDecay: number,
  limited: boolean,
): UnstackableLotResponse[] {
  if (!limited) return lots.slice(0, 1);
  const tolerance = Number.EPSILON * Math.max(1, requiredDecay) * 4;
  let total = 0;
  const lastNeeded = lots.findIndex((lot) => {
    total += toPositiveNumber(lot.tt);
    return total + tolerance >= requiredDecay;
  });
  return lastNeeded < 0 ? lots : lots.slice(0, lastNeeded + 1);
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

/** Estimate costs and finder depth from the selected equipment and report invalid selections. */
export function calculateMiningSession(
  values: MiningSessionFormValues,
  equipment: MiningEquipment,
) {
  const { lots, finders, excavators, amplifiers, enhancers, enhancerStock } =
    equipment;
  const firstLot = lots.find((lot) => lot.id === values.finderLotIds[0]);
  const finder = finders.find((item) => item.id === firstLot?.item.id);
  const finderLots = [...new Set(values.finderLotIds)].flatMap((id) => {
    const lot = lots.find(
      (entry) => entry.id === id && entry.item.id === finder?.id,
    );
    return lot ? [lot] : [];
  });
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
      path: 'finderLotIds',
      message: 'MINING.SETUP.INCOMPLETE_FINDER',
    });
  const needsMoreFinderTt =
    finder?.details.isLimited === true &&
    finderTt + Number.EPSILON * Math.max(1, finderTt, finderDecay) * 4 <
      finderDecay;
  if (
    finder?.details.isLimited &&
    (finderLots.some((lot) => lot.tt === null) || needsMoreFinderTt)
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
  let depthBonusPercent = 0;
  for (const [field, selected, tool] of [
    ['enhancers', finderLots, 'FINDER'],
    ['excavatorEnhancers', excavatorLots, 'EXCAVATOR'],
  ] as const) {
    const tier = minimumTier(selected);
    for (const [socket, id] of Object.entries(values[field])) {
      if (!id) continue;
      const enhancer = enhancers.find((item) => item.id === id);
      if (
        !enhancer ||
        enhancer.details.tool !== tool ||
        socket !== `s${enhancer.details.socket}` ||
        enhancer.details.socket > tier ||
        (enhancerStock[id] ?? 0) < 1
      ) {
        issues.push({
          path: `${field}.${socket}`,
          message: 'MINING.SETUP.INVALID_ENHANCER',
        });
      } else if (tool === 'FINDER' && enhancer.details.type === 'DEPTH') {
        depthBonusPercent += numericValue(enhancer.details.bonus);
      }
    }
  }
  const baseDepth = parseNumber(finder?.details.depth);
  const effectiveDepth =
    baseDepth === null ? null : baseDepth * (1 + depthBonusPercent / 100);
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
  const finderAmmoByLot = Object.fromEntries(
    finderLots.map((lot) => [
      lot.id,
      finderDecay > 0 ? ammo * (finderDecayByLot[lot.id] / finderDecay) : 0,
    ]),
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
    enhancedFinderDepth: effectiveDepth === baseDepth ? null : effectiveDepth,
    finderLots,
    excavatorLots,
    amplifier,
    amplifierLots,
    finderDecay,
    finderDecayByLot,
    finderAmmoByLot,
    needsMoreFinderTt,
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
