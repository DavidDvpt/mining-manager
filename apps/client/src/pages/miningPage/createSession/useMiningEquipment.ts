import { useQueries } from '@tanstack/react-query';
import {
  useGetApiV1Finders,
  useGetApiV1FindersStock,
  useGetApiV1Excavators,
  useGetApiV1ExcavatorsStock,
  useGetApiV1FinderAmplifiers,
  useGetApiV1FinderAmplifiersStock,
  useGetApiV1Enhancers,
  getGetApiV1LotsItemIdQueryOptions,
  getGetApiV1LotsUnstackableItemItemIdQueryOptions,
} from '@/api/generated/miningManagerAPI';
import type {
  FinderResponse,
  ExcavatorResponse,
  FinderAmplifierResponse,
  UnstackableLotResponse,
  EnhancerResponse,
} from '@/api/generated/model';

export type MiningEquipment = {
  finders: FinderResponse[];
  excavators: ExcavatorResponse[];
  amplifiers: FinderAmplifierResponse[];
  enhancers: EnhancerResponse[];
  lots: UnstackableLotResponse[];
  enhancerStock: Record<string, number>;
};

/** Load owned equipment lots and enhancer stocks, exposing errors before submission. */
export function useMiningEquipment() {
  const finders = useGetApiV1Finders();
  const finderStock = useGetApiV1FindersStock();
  const excavators = useGetApiV1Excavators();
  const excavatorStock = useGetApiV1ExcavatorsStock();
  const amplifiers = useGetApiV1FinderAmplifiers();
  const amplifierStock = useGetApiV1FinderAmplifiersStock();
  const enhancers = useGetApiV1Enhancers();
  const ownedFinders = (finders.data ?? []).filter(
    (item) => item.isActive !== false && (finderStock.data?.[item.id] ?? 0) > 0,
  );
  const ownedExcavators = (excavators.data ?? []).filter(
    (item) =>
      item.isActive !== false && (excavatorStock.data?.[item.id] ?? 0) > 0,
  );
  const ownedAmplifiers = (amplifiers.data ?? []).filter(
    (item) =>
      item.isActive !== false && (amplifierStock.data?.[item.id] ?? 0) > 0,
  );
  const owned = [...ownedFinders, ...ownedExcavators, ...ownedAmplifiers];
  const lots = useQueries({
    queries: owned.map((item) =>
      getGetApiV1LotsUnstackableItemItemIdQueryOptions(item.id),
    ),
  });
  const stock = useQueries({
    queries: (enhancers.data ?? []).map((item) =>
      getGetApiV1LotsItemIdQueryOptions(item.id),
    ),
  });
  const queries = [
    finders,
    finderStock,
    excavators,
    excavatorStock,
    amplifiers,
    amplifierStock,
    enhancers,
    ...lots,
    ...stock,
  ];
  const equipment: MiningEquipment = {
    finders: ownedFinders,
    excavators: ownedExcavators,
    amplifiers: ownedAmplifiers,
    enhancers: enhancers.data ?? [],
    lots: lots
      .flatMap((query) => query.data ?? [])
      .filter((lot) => lot.isActive && lot.qty > lot.reserved),
    enhancerStock: Object.fromEntries(
      (enhancers.data ?? []).map((item, index) => [
        item.id,
        stock[index]?.data?.totalQuantity ?? 0,
      ]),
    ),
  };
  return {
    equipment,
    isPending: queries.some((query) => query.isPending),
    isError: queries.some((query) => query.isError),
  };
}
