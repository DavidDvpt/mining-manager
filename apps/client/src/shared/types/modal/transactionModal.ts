import type { ItemStoreRow } from '../listItem';

/** Supported transaction directions for the transaction modal. */
export type TransactionAction = 'buy' | 'sell';

/** Values submitted by the transaction modal pricing form. */
export type TransactionFormValues = {
  quantity: number;
  tt: number;
  fee: number;
  ttc: number;
};

/** Props required to render and submit the transaction modal. */
export type TransactionModalProps = {
  item: ItemStoreRow | null;
  action: TransactionAction;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit?: (values: TransactionFormValues) => void | Promise<void>;
};
