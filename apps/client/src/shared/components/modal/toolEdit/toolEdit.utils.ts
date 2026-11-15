import { z } from 'zod';
import { isLimitedItem } from '@/shared/utils';
import type { ItemStoreRow } from '@/shared/types/listItem';

export type ToolEditValues = {
  tier?: number;
  tt?: number;
};

/** Return whether the selected tool supports tier editing. */
export function shouldShowTier(item: ItemStoreRow | null): boolean {
  return item?.kind === 'finder' || item?.kind === 'excavator';
}

/** Return whether the selected unlimited tool supports TT editing. */
export function shouldShowTt(item: ItemStoreRow | null): boolean {
  return (
    item !== null &&
    !isLimitedItem(item) &&
    (item.kind === 'finder' ||
      item.kind === 'excavator' ||
      item.kind === 'refiner' ||
      item.kind === 'finder-amplifier')
  );
}

/** Build the validation schema using the catalogue TT ceiling. */
export function createToolEditSchema(maxTt?: number) {
  return z.object({
    tier: z.number().int().min(0).max(10).optional(),
    tt: z.number().min(0).max(maxTt ?? Number.MAX_VALUE).optional(),
  });
}
