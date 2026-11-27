import type { MiningSearchType } from '@/shared/types/mining';

const MINING_SEARCH_COST_MULTIPLIERS: Record<
  MiningSearchType,
  { decay: number; ammo: number }
> = {
  E: { decay: 1, ammo: 1 },
  O: { decay: 1, ammo: 2 },
  OE: { decay: 2, ammo: 3 },
};

/** Convert an API decimal value into a usable positive number. */
export function toPositiveNumber(value: string | null | undefined): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
}

/** Return the decay multiplier for the selected mining search mode. */
export function getMiningDecayMultiplier(searchType: MiningSearchType): number {
  return MINING_SEARCH_COST_MULTIPLIERS[searchType].decay;
}

/** Return the ammunition multiplier for the selected mining search mode. */
export function getMiningAmmoMultiplier(searchType: MiningSearchType): number {
  return MINING_SEARCH_COST_MULTIPLIERS[searchType].ammo;
}

/** Calculate amplifier clicks covered by the available stock. */
export function getAmplifierClicks(
  tt: string | null,
  decay: string | null,
  quantity: number,
  searchType: MiningSearchType,
): number {
  const costPerClick =
    toPositiveNumber(decay) * getMiningDecayMultiplier(searchType);
  if (costPerClick <= 0) return 0;
  const clicks = toPositiveNumber(tt) / costPerClick;
  return (
    Math.floor(clicks + Number.EPSILON * Math.max(1, clicks) * 4) * quantity
  );
}
