import type { TranslationKey } from '@/i18n/types';
import type { MiningSearchType } from '@/shared/types/mining';

import type { MiningButtonId } from './constants';

type Translate = (key: TranslationKey) => string;

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
  return costPerClick > 0
    ? Math.floor((toPositiveNumber(tt) * quantity) / costPerClick)
    : 0;
}

/** Resolve the URL page into the page that can currently be rendered. */
export function getMiningActivePage(
  page: MiningButtonId | undefined,
  hasCurrentSession: boolean,
): MiningButtonId {
  if (page === 'create-session') return page;
  if (hasCurrentSession && (page === 'current-session' || page === 'close')) {
    return page;
  }

  return 'sessions-list';
}

/** Translate the selected mining navigation page for the active-view label. */
export function getMiningActiveView(
  page: MiningButtonId,
  t: Translate,
): string {
  switch (page) {
    case 'create-session':
      return t('MINING.CREATE_SESSION');
    case 'current-session':
      return t('MINING.CURRENT_SESSION');
    case 'close':
      return t('MINING.CLOSE');
    case 'sessions-list':
      return t('MINING.SESSIONS_LIST');
  }
}
