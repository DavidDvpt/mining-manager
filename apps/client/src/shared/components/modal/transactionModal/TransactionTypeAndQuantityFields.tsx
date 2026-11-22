import { CreateStackableBuyRequestTypeDetail } from '@/api/generated/model/createStackableBuyRequestTypeDetail';
import { useTranslations } from '@/i18n/useTranslations';
import { InputRHF } from '@/shared/components/form/InputRHF';
import { SelectRHF } from '@/shared/components/form/SelectRHF';
import styles from './transaction-modal.module.scss';

type TransactionTypeAndQuantityFieldsProps = {
  action: 'buy' | 'sell';
  isStackable: boolean;
};

/** Render the transaction type and, when applicable, purchase quantity fields. */
export function TransactionTypeAndQuantityFields({
  action,
  isStackable,
}: TransactionTypeAndQuantityFieldsProps): import('react').JSX.Element {
  const { t } = useTranslations();
  const labels: Record<string, string> = {
    TT: 'TT',
    AUCTION: 'Auction',
    HAND_TO_HAND: t('TRANSACTION_MODAL.TYPE_DETAIL_HAND_TO_HAND'),
    FOUND: t('TRANSACTION_MODAL.TYPE_DETAIL_FOUND'),
    GIFT: t('TRANSACTION_MODAL.TYPE_DETAIL_GIFT'),
    EXISTING_STOCK: t('TRANSACTION_MODAL.TYPE_DETAIL_EXISTING_STOCK'),
    GIVEN: t('TRANSACTION_MODAL.TYPE_DETAIL_GIVEN'),
  };

  return (
    <div className={styles.typeDetailFields}>
      <SelectRHF
        name="type_detail"
        label={t('TRANSACTION_MODAL.TYPE_DETAIL')}
        className={styles.typeDetailSelect}
        options={Object.values(CreateStackableBuyRequestTypeDetail).map(
          (value): { value: string; label: string } => ({
            value,
            label: labels[value],
          }),
        )}
      />
      {action === 'buy' && !isStackable ? (
        <InputRHF
          name="purchase_quantity"
          label={t('TRANSACTION_MODAL.PURCHASE_QUANTITY')}
          type="number"
          min={1}
          step={1}
        />
      ) : null}
    </div>
  );
}

export default TransactionTypeAndQuantityFields;
