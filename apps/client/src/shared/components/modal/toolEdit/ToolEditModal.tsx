import { useMemo, useRef, useState } from 'react';
import {
  getGetApiV1LotsUnstackableItemItemIdQueryKey,
  getGetApiV1LotsItemIdQueryKey,
  useGetApiV1LotsUnstackableItemItemId,
  usePutApiV1LotsUnstackableLotId,
} from '@/api/generated/miningManagerAPI';
import { FormButtonsSection, GenericForm, InputRHF } from '@/shared/components';
import { Modal } from '@/shared/components/modal';
import { useQueryClient } from '@tanstack/react-query';
import { useTranslations } from '@/i18n/useTranslations';
import type { ItemRow } from '@/shared/types/listItem';
import styles from './tool-edit-modal.module.scss';
import {
  createToolEditSchema,
  shouldShowTier,
  shouldShowTt,
  type ToolEditValues,
} from './toolEdit.utils';
import ToolEditFieldLabel from './ToolEditFieldLabel';
import { TransactionModalInfo } from '../transactionModal/TransactionModalInfo';
import { isAvailableTransactionLot } from '../transactionModal/transactionModal.utils';

type ToolEditModalProps = {
  item: ItemRow | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

/** Show current TT and tier, enable supported edits, validate input, and persist the owned tool lot. */
export function ToolEditModal({
  item,
  open,
  onOpenChange,
}: ToolEditModalProps): import('react').JSX.Element | null {
  const { t } = useTranslations();
  const queryClient = useQueryClient();
  const updateLot = usePutApiV1LotsUnstackableLotId();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const submitting = useRef(false);
  const lotsQuery = useGetApiV1LotsUnstackableItemItemId(item?.id ?? '', {
    query: {
      queryKey: getGetApiV1LotsUnstackableItemItemIdQueryKey(item?.id ?? ''),
      enabled: open && item !== null,
    },
  });
  const lot =
    lotsQuery.data?.find((candidate): boolean =>
      isAvailableTransactionLot(candidate, item?.id ?? ''),
    ) ?? null;
  const canEditTier = shouldShowTier(item);
  const canEditTt = shouldShowTt(item);
  const maxTt = item?.tt ?? undefined;
  const schema = useMemo(
    () =>
      createToolEditSchema(maxTt).superRefine((values, context): void => {
        for (const field of ['tt', 'tier'] as const) {
          if (
            (field === 'tt' ? canEditTt : canEditTier) &&
            values[field] === undefined
          ) {
            context.addIssue({
              code: 'custom',
              path: [field],
              message: t('TOOL_EDIT_MODAL.REQUIRED'),
            });
          }
        }
      }),
    [maxTt, canEditTt, canEditTier, t],
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

  /** Prevent dismissal while the current lot update is in flight. */
  const close = (): void => {
    if (!submitting.current) onOpenChange(false);
  };

  /** Persist supported attributes once; retain the draft and expose errors for retry. */
  const handleSubmit = async (values: ToolEditValues): Promise<void> => {
    if (!lot || submitting.current) return;
    submitting.current = true;
    setPending(true);
    setError(null);
    try {
      await updateLot.mutateAsync({
        lotId: lot.id,
        data: {
          tier: canEditTier ? values.tier : undefined,
          tt: canEditTt ? values.tt : undefined,
        },
      });
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: getGetApiV1LotsUnstackableItemItemIdQueryKey(item.id),
        }),
        queryClient.invalidateQueries({
          queryKey: getGetApiV1LotsItemIdQueryKey(item.id),
        }),
      ]);
      onOpenChange(false);
    } catch (failure) {
      setError(
        failure instanceof Error ? failure.message : t('TOOL_EDIT_MODAL.ERROR'),
      );
    } finally {
      submitting.current = false;
      setPending(false);
    }
  };

  return (
    <Modal
      open={open}
      onOpenChange={(nextOpen): void => {
        if (!nextOpen) close();
      }}
      title={t('ITEM_STORE.EDIT')}
      description={item.name}
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
            tier: lot.tier ?? 0,
            tt: Number(lot.tt ?? item.tt ?? 0),
          }}
          onSubmit={handleSubmit}
          className={styles.form}
        >
          <TransactionModalInfo
            item={{ ...item, ttRemaining: Number(lot.tt ?? item.tt ?? 0) }}
          />
          {error ? (
            <p role="alert" className={styles.validationError}>
              {error}
            </p>
          ) : null}
          <fieldset disabled={pending} className={styles.fields}>
            <InputRHF
              name="tt"
              label={ttLabel}
              type="number"
              min={0}
              max={maxTt}
              step="any"
              disabled={!canEditTt}
            />
            <InputRHF
              name="tier"
              label={tierLabel}
              type="number"
              min={0}
              max={10}
              step={1}
              disabled={!canEditTier}
            />
          </fieldset>
          <FormButtonsSection
            onCancel={close}
            cancelLabel={t('TOOL_EDIT_MODAL.CANCEL')}
            submitLabel={
              pending ? t('TOOL_EDIT_MODAL.SAVING') : t('TOOL_EDIT_MODAL.SAVE')
            }
            submitDisabled={pending}
            cancelDisabled={pending}
            align="right"
          />
        </GenericForm>
      )}
    </Modal>
  );
}

export default ToolEditModal;
