import { EntropiaImage } from '@/shared/components/entropiaImage';
import { formatDecimalValue } from '@/shared/utils';
import type { ItemStoreRow } from '@/shared/types/listItem';
import type { TransactionLot } from '@/shared/types/modal';
import styles from './transaction-modal.module.scss';

type TransactionModalInfoProps = {
  item: ItemStoreRow | null;
  lot: TransactionLot | null;
};

/** Render the selected item information displayed in the transaction modal. */
export function TransactionModalInfo({ item, lot }: TransactionModalInfoProps) {
  const name = item?.name ?? lot?.item.name ?? 'Item';
  const imageUrl = item?.imageUrl ?? null;
  const tt = lot?.tt_remaining ?? lot?.tt ?? item?.tt ?? null;

  return (
    <div className={styles.itemInfo}>
      <EntropiaImage url={imageUrl} alt={name} size="small" />
      <div className={styles.itemDetails}>
        <strong>{name}</strong>
        <span>TT : {formatDecimalValue(tt)}</span>
      </div>
    </div>
  );
}

export default TransactionModalInfo;
