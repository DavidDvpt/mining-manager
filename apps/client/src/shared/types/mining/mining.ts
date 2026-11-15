/** Supported mining resource search modes. */
export type MiningSearchType = 'E' | 'O' | 'OE';

/** Values collected by the mining-session configuration form. */
export type MiningSessionFormValues = {
  clicks: number;
  searchType: MiningSearchType;
  planet: string;
  zone: string;
  finderItemId: string;
  finderLotIds: string[];
  amplifierIds: string[];
  enhancers: Record<string, string>;
};
