import type { ItemRow } from '../listItem';
import type { CreateStackableBuyRequestTypeDetail } from '@/api/generated/model/createStackableBuyRequestTypeDetail';
import type { UnstackableLotResponse } from '@/api/generated/model/unstackableLotResponse';
import type { ReactNode } from 'react';

/** API lot shape accepted by the transaction modal, including remaining TT when provided. */
export type TransactionLot = UnstackableLotResponse & {
  ttRemaining?: string | null;
};

/** Normalized transaction entity passed to the shared transaction modal. */
export type TransactionItem = ItemRow & {
  ttRemaining?: number | string | null;
};

/** Supported transaction directions for the transaction modal. */
export type TransactionAction = 'buy' | 'sell';

/** API item category used when creating a transaction. */
export type TransactionKind = 'tool' | 'enhancer' | 'material';

/** Values submitted by the transaction modal pricing form. */
export type TransactionFormValues = {
  quantity: number;
  tt: number;
  fee: number;
  ttc: number;
  type_detail: CreateStackableBuyRequestTypeDetail;
  purchase_quantity: number;
};

/** Props required to render and submit the transaction modal. */
export type TransactionModalProps = {
  item: TransactionItem | null;
  action: TransactionAction;
  onClose: () => void;
  onSubmit: (values: TransactionFormValues) => Promise<void>;
  validationError?: string | null;
  children: ReactNode;
};
