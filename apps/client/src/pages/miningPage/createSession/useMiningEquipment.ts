import { useQueries } from '@tanstack/react-query';
import {
  useGetApiV1FindersLots,
  getGetApiV1FindersLotsQueryKey,
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
  const finderInventory = useGetApiV1FindersLots({
    query: { queryKey: getGetApiV1FindersLotsQueryKey(), staleTime: 0 },
  });
  const excavators = useGetApiV1Excavators();
  const excavatorStock = useGetApiV1ExcavatorsStock();
  const amplifiers = useGetApiV1FinderAmplifiers();
  const amplifierStock = useGetApiV1FinderAmplifiersStock();
  const enhancers = useGetApiV1Enhancers();
  const finderGroups = Object.values(finderInventory.data ?? {});
  const ownedExcavators = (excavators.data ?? []).filter(
    (item) =>
      item.isActive !== false && (excavatorStock.data?.[item.id] ?? 0) > 0,
  );
  const ownedAmplifiers = (amplifiers.data ?? []).filter(
    (item) =>
      item.isActive !== false && (amplifierStock.data?.[item.id] ?? 0) > 0,
  );
  const owned = [...ownedExcavators, ...ownedAmplifiers];
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
    finderInventory,
    excavators,
    excavatorStock,
    amplifiers,
    amplifierStock,
    enhancers,
    ...lots,
    ...stock,
  ];
  const equipment: MiningEquipment = {
    finders: finderGroups.flatMap((group) => (group[0] ? [group[0].item] : [])),
    excavators: ownedExcavators,
    amplifiers: ownedAmplifiers,
    enhancers: enhancers.data ?? [],
    lots: [
      ...finderGroups.flat(),
      ...lots.flatMap((query) => query.data ?? []),
    ].filter((lot) => lot.isActive && lot.qty > lot.reserved),
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
