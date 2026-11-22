import { EntropiaImage } from '@/shared/components/entropiaImage';
import { formatDecimalValue } from '@/shared/utils';
import type { TransactionItem } from '@/shared/types/modal';
import styles from './transaction-modal.module.scss';

type TransactionModalInfoProps = {
  item: TransactionItem | null;
};

/** Render the selected item information displayed in the transaction modal. */
export function TransactionModalInfo({
  item,
}: TransactionModalInfoProps): import('react').JSX.Element {
  const name = item?.name ?? 'Item';
  const imageUrl = item?.imageUrl ?? null;
  const tt = item?.ttRemaining ?? item?.tt ?? null;

  return (
    <div className={styles.itemInfo}>
      <EntropiaImage url={imageUrl} alt={name} size="small" />

      <div className={styles.itemDetails}>
        <strong>{name}</strong>
        <span>TT : {formatDecimalValue(tt)}</span>
        <span>Stock : {item?.stock ?? '—'}</span>
      </div>
    </div>
  );
}

export default TransactionModalInfo;
