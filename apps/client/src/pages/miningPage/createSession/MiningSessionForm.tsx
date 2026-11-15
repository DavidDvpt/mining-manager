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
export function MiningSessionForm() {
  const { t } = useTranslations();
  const findersQuery = useGetApiV1Finders();
  const finderStockQuery = useGetApiV1FindersStock();
  const amplifiersQuery = useGetApiV1FinderAmplifiers();
  const amplifierStockQuery = useGetApiV1FinderAmplifiersStock();
  const enhancersQuery = useGetApiV1Enhancers();
  const allEnhancers = useMemo(
    () => enhancersQuery.data ?? [],
    [enhancersQuery.data],
  );
  const enhancerStockQueries = useQueries({
    queries: allEnhancers.map((enhancer) =>
      getGetApiV1LotsItemIdQueryOptions(enhancer.id),
    ),
  });
  const enhancerStock = useMemo(
    () =>
      Object.fromEntries(
        allEnhancers.map((enhancer, index) => [
          enhancer.id,
          enhancerStockQueries[index]?.data?.total_quantity ?? 0,
        ]),
      ),
    [allEnhancers, enhancerStockQueries],
  );
  const finders = useMemo(
    () =>
      (findersQuery.data ?? []).filter(
        (finder) =>
          finder.is_active !== false &&
          (finderStockQuery.data?.[finder.id] ?? 0) > 0,
      ),
    [findersQuery.data, finderStockQuery.data],
  );
  const amplifiers = useMemo(
    () =>
      (amplifiersQuery.data ?? []).filter(
        (amplifier) =>
          amplifier.is_active !== false &&
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
          (enhancer) => (enhancerStock[enhancer.id] ?? 0) > 0,
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
