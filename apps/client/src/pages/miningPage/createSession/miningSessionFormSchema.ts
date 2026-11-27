import { z } from 'zod';

import type { MiningSessionFormValues } from '@/shared/types/mining';

/** Validate values collected by the mining-session configuration form. */
export const miningSessionFormSchema: z.ZodType<
  MiningSessionFormValues,
  MiningSessionFormValues
> = z.object({
  clicks: z.number().int().min(1, 'At least one click is required.'),
  searchType: z.enum(['E', 'O', 'OE']),
  planet: z.string().trim().min(1, 'A planet is required.'),
  zone: z.string().trim(),
  finderLotIds: z.array(z.string()).min(1, 'Select at least one finder.'),
  amplifierItemId: z.string(),
  excavatorLotIds: z.array(z.string()).min(1, 'Select at least one excavator.'),
  excavatorEnhancers: z.record(z.string(), z.string()),
  enhancers: z.record(z.string(), z.string()),
}) as z.ZodType<MiningSessionFormValues, MiningSessionFormValues>;

/** Provide the initial values for a new mining-session configuration. */
export const miningSessionFormDefaultValues: MiningSessionFormValues = {
  clicks: 1,
  searchType: 'E',
  planet: '',
  zone: '',
  finderLotIds: [],
  amplifierItemId: '',
  excavatorLotIds: [],
  excavatorEnhancers: {},
  enhancers: {},
};
