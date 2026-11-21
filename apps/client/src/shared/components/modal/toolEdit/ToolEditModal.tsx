import { useMemo } from 'react';
import {
  getGetApiV1LotsUnstackableItemItemIdQueryKey,
  useGetApiV1LotsUnstackableItemItemId,
  usePutApiV1LotsUnstackableLotId,
} from '@/api/generated/miningManagerAPI';
import { FormButtonsSection, GenericForm, InputRHF } from '@/shared/components';
import { Modal } from '@/shared/components/modal';
import { useQueryClient } from '@tanstack/react-query';
import { useTranslations } from '@/i18n/useTranslations';
import type { ItemStoreRow } from '@/shared/types/listItem';
import styles from './tool-edit-modal.module.scss';
import {
  createToolEditSchema,
  shouldShowTier,
  shouldShowTt,
  type ToolEditValues,
} from './toolEdit.utils';
import ToolEditFieldLabel from './ToolEditFieldLabel';

type ToolEditModalProps = {
  item: ItemStoreRow | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

/** Edit the mutable attributes of the first owned lot for a catalogue tool. */
export function ToolEditModal({
  item,
  open,
  onOpenChange,
}: ToolEditModalProps): import('react').JSX.Element | null {
  const { t } = useTranslations();
  const queryClient = useQueryClient();
  const updateLot = usePutApiV1LotsUnstackableLotId();
  const lotsQuery = useGetApiV1LotsUnstackableItemItemId(item?.id ?? '', {
    query: {
      queryKey: getGetApiV1LotsUnstackableItemItemIdQueryKey(item?.id ?? ''),
      enabled: open && item !== null,
    },
  });
  const lot = lotsQuery.data?.[0] ?? null;
  const showTier = shouldShowTier(item);
  const showTt = shouldShowTt(item);
  const maxTt = item?.tt ?? undefined;
  const schema = useMemo(
    (): import('zod').ZodObject<
      {
        tier: import('zod').ZodOptional<import('zod').ZodNumber>;
        tt: import('zod').ZodOptional<import('zod').ZodNumber>;
      },
      import('zod/v4/core').$strip
    > => createToolEditSchema(maxTt),
    [maxTt],
  );
  const tierLabel = useMemo(
    (): import('react').JSX.Element => (
      <ToolEditFieldLabel range="0 - 10">Tier</ToolEditFieldLabel>
    ),
    [],
  );
  const ttLabel = useMemo(
    (): import('react').JSX.Element => (
      <ToolEditFieldLabel range={`0 - ${maxTt ?? '—'}`}>TT</ToolEditFieldLabel>
    ),
    [maxTt],
  );

  if (!item) return null;

  const handleSubmit = async (values: ToolEditValues): Promise<void> => {
    if (!lot) return;
    await updateLot.mutateAsync({
      lotId: lot.id,
      data: {
        tier: showTier ? values.tier : undefined,
        tt: showTt ? values.tt : undefined,
      },
    });
    await queryClient.invalidateQueries({
      queryKey: getGetApiV1LotsUnstackableItemItemIdQueryKey(item.id),
    });
    onOpenChange(false);
  };

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={`${t('TOOL_EDIT_MODAL.TITLE')} : ${item.name}`}
    >
      {lotsQuery.isLoading ? (
        <p>{t('TOOL_EDIT_MODAL.LOADING')}</p>
      ) : lotsQuery.isError || !lot ? (
        <p role="alert">{t('TOOL_EDIT_MODAL.ERROR')}</p>
      ) : (
        <GenericForm<ToolEditValues>
          key={lot.id}
          schema={schema}
          defaultValues={{
            tier: showTier ? (lot.tier ?? 0) : undefined,
            tt: showTt && lot.tt !== null ? Number(lot.tt) : undefined,
          }}
          onSubmit={handleSubmit}
          className={styles.form}
        >
          <div className={styles.fields}>
            {showTier ? (
              <InputRHF
                name="tier"
                label={tierLabel}
                type="number"
                min={0}
                max={10}
                step={1}
                className={styles.compactInput}
              />
            ) : null}
            {showTt ? (
              <InputRHF
                name="tt"
                label={ttLabel}
                type="number"
                min={0}
                max={maxTt}
                step="any"
                className={styles.compactInput}
              />
            ) : null}
          </div>
          <FormButtonsSection
            onCancel={(): void => onOpenChange(false)}
            cancelLabel={t('TOOL_EDIT_MODAL.CANCEL')}
            submitLabel={
              updateLot.isPending
                ? t('TOOL_EDIT_MODAL.SAVING')
                : t('TOOL_EDIT_MODAL.SAVE')
            }
            submitDisabled={updateLot.isPending}
          />
        </GenericForm>
      )}
    </Modal>
  );
}

export default ToolEditModal;
