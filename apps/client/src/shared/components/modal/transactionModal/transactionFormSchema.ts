import { z } from 'zod';
import { CreateStackableBuyRequestTypeDetail } from '@/api/generated/model/createStackableBuyRequestTypeDetail';

/** Validate the numeric values submitted by the transaction form. */
export const transactionFormSchema = z.object({
  quantity: z.number().min(1),
  tt: z.number().min(0),
  fee: z.number().min(0),
  ttc: z.number().min(0),
  type_detail: z.enum(CreateStackableBuyRequestTypeDetail),
  purchase_quantity: z.number().int().min(1),
});

export type TransactionFormType = z.infer<typeof transactionFormSchema>;
