export const ITEM_ROUTES = {
  materials: 'material',
  finders: 'finder',
  excavators: 'excavator',
  refiners: 'refiner',
  amplifiers: 'finder-amplifier',
  'finder-enhancers': 'finder-enhancer',
  'excavator-enhancers': 'excavator-enhancer',
} as const;

export const ITEM_SUB_ROUTES = {
  'animal-oil': 'Animal Oil',
  consumable: 'Consumable',
  enmatter: 'Enmatter',
  'refined-enmatter': 'Refined Enmatter',
  ore: 'Ore',
  'refined-ore': 'Refined Ore',
  food: 'Food',
  strongboxe: 'Strongboxes',
  'natural-material': 'Natural Material',
} as const;

export type ItemKind = (typeof ITEM_ROUTES)[keyof typeof ITEM_ROUTES];
export type ItemSubKind =
  (typeof ITEM_SUB_ROUTES)[keyof typeof ITEM_SUB_ROUTES];
