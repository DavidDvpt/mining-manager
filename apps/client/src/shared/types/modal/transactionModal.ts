import type { ItemRow } from '../listItem';
import type { UnstackableLotResponse } from '@/api/generated/model/unstackableLotResponse';

/** API lot shape accepted by the transaction modal, including remaining TT when provided. */
export type TransactionLot = UnstackableLotResponse & {
  ttRemaining?: string | null;
};

/** Supported transaction directions for the transaction modal. */
export type TransactionAction = 'buy' | 'sell';

/** Values submitted by the transaction modal pricing form. */
export type TransactionFormValues = {
  quantity: number;
  tt: number;
  fee: number;
  ttc: number;
  autoCompute: boolean;
};

/** Props required to render and submit the transaction modal. */
export type TransactionModalProps = {
  item: ItemRow | null;
  lot: TransactionLot | null;
  lots?: TransactionLot[];
  action: TransactionAction;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};
