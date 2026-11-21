import { useMemo } from 'react';
import { useQueries } from '@tanstack/react-query';

import { FormButtonsSection, GenericForm } from '@/shared/components';
import {
  getGetApiV1LotsItemIdQueryOptions,
  useGetApiV1Enhancers,
  useGetApiV1FinderAmplifiers,
  useGetApiV1FinderAmplifiersStock,
  useGetApiV1Finders,
  useGetApiV1FindersStock,
} from '@/api/generated/miningManagerAPI';
import { useTranslations } from '@/i18n/useTranslations';
import type { MiningSessionFormValues } from '@/shared/types/mining';

import MiningSessionFormContent from './MiningSessionFormContent';
import {
  miningSessionFormDefaultValues,
  miningSessionFormSchema,
} from './miningSessionFormSchema';
import styles from './mining-session-form.module.scss';

/** Submit the validated configuration preview until session creation is wired. */
function handleMiningSessionSubmit(_values: MiningSessionFormValues): void {
  // The create-session API mutation will be connected in the next step.
}

/** Render the RHF/Zod mining-session configuration form and its subsections. */
export function MiningSessionForm(): import('react').JSX.Element {
  const { t } = useTranslations();
  const findersQuery = useGetApiV1Finders();
  const finderStockQuery = useGetApiV1FindersStock();
  const amplifiersQuery = useGetApiV1FinderAmplifiers();
  const amplifierStockQuery = useGetApiV1FinderAmplifiersStock();
  const enhancersQuery = useGetApiV1Enhancers();
  const allEnhancers = useMemo(
    (): import('../../../api/generated/model').EnhancerResponse[] =>
      enhancersQuery.data ?? [],
    [enhancersQuery.data],
  );
  const enhancerStockQueries = useQueries({
    queries: allEnhancers.map(
      (
        enhancer,
      ): import('@tanstack/react-query').UseQueryOptions<
        import('../../../api/generated/model').LotCollectionResponse,
        import('../../../lib/axios/types').ApiError,
        import('../../../api/generated/model').LotCollectionResponse,
        readonly unknown[]
      > & { queryKey: import('@tanstack/query-core').QueryKey } =>
        getGetApiV1LotsItemIdQueryOptions(enhancer.id),
    ),
  });
  const enhancerStock = useMemo(
    (): { [k: string]: any } =>
      Object.fromEntries(
        allEnhancers.map((enhancer, index): [string, any] => [
          enhancer.id,
          enhancerStockQueries[index]?.data?.totalQuantity ?? 0,
        ]),
      ),
    [allEnhancers, enhancerStockQueries],
  );
  const finders = useMemo(
    (): import('../../../api/generated/model').FinderResponse[] =>
      (findersQuery.data ?? []).filter(
        (finder): boolean =>
          finder.isActive !== false &&
          (finderStockQuery.data?.[finder.id] ?? 0) > 0,
      ),
    [findersQuery.data, finderStockQuery.data],
  );
  const amplifiers = useMemo(
    (): import('../../../api/generated/model').FinderAmplifierResponse[] =>
      (amplifiersQuery.data ?? []).filter(
        (amplifier): boolean =>
          amplifier.isActive !== false &&
          (amplifierStockQuery.data?.[amplifier.id] ?? 0) > 0,
      ),
    [amplifiersQuery.data, amplifierStockQuery.data],
  );

  return (
    <GenericForm<MiningSessionFormValues>
      schema={miningSessionFormSchema}
      defaultValues={miningSessionFormDefaultValues}
      onSubmit={handleMiningSessionSubmit}
      className={styles.form}
    >
      <MiningSessionFormContent
        finders={finders}
        finderStock={finderStockQuery.data ?? {}}
        amplifiers={amplifiers}
        amplifierStock={amplifierStockQuery.data ?? {}}
        enhancers={allEnhancers.filter(
          (enhancer): boolean => (enhancerStock[enhancer.id] ?? 0) > 0,
        )}
        enhancerStock={enhancerStock}
      />
      <FormButtonsSection
        cancelVisible={false}
        submitLabel={t('MINING.CREATE_SESSION')}
      />
    </GenericForm>
  );
}

export default MiningSessionForm;
