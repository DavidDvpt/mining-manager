import type { ItemRow } from '../listItem';
import type { CreateStackableBuyRequestTypeDetail } from '@/api/generated/model/createStackableBuyRequestTypeDetail';
import type { UnstackableLotResponse } from '@/api/generated/model/unstackableLotResponse';

/** Owned equipment instance; the API exposes its remaining TT as `tt`. */
export type TransactionLot = UnstackableLotResponse;

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
  autoCompute: boolean;
};

/** Props required to render and submit the transaction modal. */
export type TransactionModalProps = {
  item: TransactionItem;
  onClose: () => void;
  onSubmit: (values: TransactionFormValues) => Promise<void>;
  stock?: number;
} & ({ action: 'buy'; lot?: never } | { action: 'sell'; lot?: TransactionLot });
