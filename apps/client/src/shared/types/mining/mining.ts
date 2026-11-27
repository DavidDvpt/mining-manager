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
  amplifierItemId: string;
  excavatorLotIds: string[];
  excavatorEnhancers: Record<string, string>;
  enhancers: Record<string, string>;
};
