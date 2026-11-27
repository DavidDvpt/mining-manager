import { useTranslations } from '@/i18n/useTranslations';
import { Navigate, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { GenericForm, Modal } from '@/shared/components';
import {
  getGetApiV1MiningCurrentQueryKey,
  useGetApiV1MiningCurrent,
  usePostApiV1MiningCreate,
} from '@/api/generated/miningManagerAPI';
import type { MiningSessionFormValues } from '@/shared/types/mining';
import MiningSessionFormContent from './MiningSessionFormContent';
import {
  miningSessionFormDefaultValues,
  miningSessionFormSchema,
} from './miningSessionFormSchema';
import { useMiningEquipment } from './useMiningEquipment';
import { calculateMiningSession } from './miningSessionCalculation';
import styles from './mining-session-form.module.scss';

/** Open creation from its URL and persist a validated owned setup through the existing API. */
export function MiningSessionForm(): import('react').JSX.Element {
  const { t } = useTranslations();
  const navigate = useNavigate();
  const client = useQueryClient();
  const current = useGetApiV1MiningCurrent();
  const { equipment, isPending, isError } = useMiningEquipment();
  const mutation = usePostApiV1MiningCreate();
  /** Close the route-controlled modal when no request is being persisted. */
  const close = (): void => {
    if (!mutation.isPending) navigate('/mining');
  };
  /** Validate current stock and capacities before mapping form fields to the existing API contract. */
  const submit = async (values: MiningSessionFormValues): Promise<void> => {
    const estimate = calculateMiningSession(values, equipment);
    if (
      estimate.issues.length ||
      current.data ||
      current.isPending ||
      current.isError
    )
      return;
    try {
      const created = await mutation.mutateAsync({
        data: {
          clics: values.clicks,
          searchType: values.searchType === 'OE' ? 'EO' : values.searchType,
          finder: values.finderLotIds,
          excavators: values.excavatorLotIds,
          sessionZone: values.zone || null,
          finderAmplifiers: estimate.amplifierLots.map((lot) => lot.id),
          finderEnhancers: Object.fromEntries(
            Object.entries(values.enhancers).filter(([, id]) => Boolean(id)),
          ),
          excavatorEnhancers: Object.fromEntries(
            Object.entries(values.excavatorEnhancers).filter(([, id]) =>
              Boolean(id),
            ),
          ),
        },
      });
      await client.invalidateQueries({
        queryKey: getGetApiV1MiningCurrentQueryKey(),
      });
      navigate(`/mining/${created.sessionId}/running`);
    } catch {
      // React Query exposes the server error below; retain the configuration for correction.
      await client.invalidateQueries({
        queryKey: getGetApiV1MiningCurrentQueryKey(),
      });
    }
  };
  if (current.data)
    return <Navigate to={`/mining/${current.data.id}/running`} replace />;
  return (
    <Modal
      open
      onOpenChange={(open) => {
        if (!open) close();
      }}
      noClose={mutation.isPending}
      title={t('MINING.SETUP.TITLE')}
      className={styles.modal}
    >
      {isPending || current.isPending ? (
        <p role="status">{t('MINING.SETUP.LOADING')}</p>
      ) : isError || current.isError ? (
        <p role="alert">{t('MINING.SETUP.LOAD_ERROR')}</p>
      ) : (
        <GenericForm<MiningSessionFormValues>
          schema={miningSessionFormSchema.superRefine((values, context) => {
            for (const issue of calculateMiningSession(values, equipment)
              .issues)
              context.addIssue({
                code: 'custom',
                path: issue.path.split('.'),
                message: t(issue.message),
              });
          })}
          defaultValues={miningSessionFormDefaultValues}
          onSubmit={submit}
          className={styles.form}
        >
          <MiningSessionFormContent
            equipment={equipment}
            onCancel={close}
            pending={mutation.isPending}
          />
          {mutation.error && (
            <p role="alert" className={styles.error}>
              {mutation.error.message}
            </p>
          )}
        </GenericForm>
      )}
    </Modal>
  );
}
export default MiningSessionForm;
