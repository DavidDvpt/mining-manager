import { z } from 'zod';
import { useFormContext, useWatch } from 'react-hook-form';
import { Modal } from '@/shared/components/modal';
import { GenericForm } from '@/shared/components/form/GenericForm';
import { FormButtonsSection } from '@/shared/components/form/FormButtonsSection';
import { RadioRHF, RadioRHFItem } from '@/shared/components/form/RadioRHF';
import { EntropiaImage } from '@/shared/components/entropiaImage';
import { getItemImageUrl } from '@/config/images';
import { formatDecimalValue } from '@/shared/utils';
import { useTranslations } from '@/i18n/useTranslations';
import type { TransactionItem, TransactionLot } from '@/shared/types/modal';
import { isAvailableTransactionLot } from '../transactionModal/transactionModal.utils';
import styles from './item-choice-modal.module.scss';

type ChoiceValues = { lotId: string };
type ItemChoiceModalProps = {
  item: TransactionItem;
  lots: TransactionLot[];
  onCancel: () => void;
  onConfirm: (lotId: string) => void;
};

/** Disable confirmation until the form selection still identifies an available instance. */
function ChoiceButtons({
  lots,
  onCancel,
}: Pick<
  ItemChoiceModalProps,
  'lots' | 'onCancel'
>): import('react').JSX.Element {
  const lotId = useWatch<ChoiceValues>({ name: 'lotId' });
  const {
    formState: { isSubmitting },
  } = useFormContext<ChoiceValues>();
  const { t } = useTranslations();
  return (
    <FormButtonsSection
      onCancel={onCancel}
      cancelLabel={t('TOOL_EDIT_MODAL.CANCEL')}
      submitLabel={t('TRANSACTION_MODAL.CONFIRM')}
      submitDisabled={
        isSubmitting || !lots.some((lot): boolean => lot.id === lotId)
      }
    />
  );
}

/** Select exactly one owned instance; submit only its ID after validating current availability. */
export function ItemChoiceModal({
  item,
  lots,
  onCancel,
  onConfirm,
}: ItemChoiceModalProps): import('react').JSX.Element {
  const { t } = useTranslations();
  const availableLots = lots.filter((lot): boolean =>
    isAvailableTransactionLot(lot, item.id),
  );
  const schema = z.object({
    lotId: z
      .string()
      .min(1)
      .refine((id): boolean =>
        availableLots.some((lot): boolean => lot.id === id),
      ),
  });
  return (
    <Modal
      open
      onOpenChange={(open): void => {
        if (!open) onCancel();
      }}
      title={t('TRANSACTION_MODAL.CHOOSE_INSTANCE')}
    >
      <GenericForm<ChoiceValues>
        schema={schema}
        defaultValues={{ lotId: '' }}
        onSubmit={({ lotId }): void => onConfirm(lotId)}
      >
        {availableLots.length === 0 ? (
          <p role="alert">{t('TRANSACTION_MODAL.UNAVAILABLE')}</p>
        ) : null}
        <RadioRHF
          name="lotId"
          className={styles.list}
          aria-label={t('TRANSACTION_MODAL.CHOOSE_INSTANCE')}
        >
          {availableLots.map((lot): import('react').JSX.Element => (
            <RadioRHFItem
              key={lot.id}
              value={lot.id}
              className={styles.row}
            >
              <EntropiaImage
                url={getItemImageUrl(lot.item.imgId)}
                alt={lot.item.name}
                size="small"
              />
              <span>
                {lot.item.name}
                {lot.tier !== null ? ` · T${lot.tier}` : ''}
              </span>
              <span>TT: {formatDecimalValue(lot.tt)}</span>
            </RadioRHFItem>
          ))}
        </RadioRHF>
        <ChoiceButtons lots={availableLots} onCancel={onCancel} />
      </GenericForm>
    </Modal>
  );
}
