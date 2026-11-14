import { z } from 'zod';

/** Validate the numeric values submitted by the transaction form. */
export const transactionFormSchema = z.object({
  quantity: z.number().min(1),
  tt: z.number().min(0),
  fee: z.number().min(0),
  ttc: z.number().min(0),
  auction: z.boolean(),
});
