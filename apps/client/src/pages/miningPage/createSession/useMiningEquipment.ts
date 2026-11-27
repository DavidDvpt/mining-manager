import { useQueries } from '@tanstack/react-query';
import {
  useGetApiV1FindersLots,
  getGetApiV1FindersLotsQueryKey,
  useGetApiV1ExcavatorsLots,
  getGetApiV1ExcavatorsLotsQueryKey,
  useGetApiV1FinderAmplifiersLots,
  getGetApiV1FinderAmplifiersLotsQueryKey,
  useGetApiV1Enhancers,
  getGetApiV1LotsItemIdQueryOptions,
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

/** Load available lots grouped by model for each tool category, along with enhancer stocks. */
export function useMiningEquipment() {
  const finderInventory = useGetApiV1FindersLots({
    query: { queryKey: getGetApiV1FindersLotsQueryKey(), staleTime: 0 },
  });
  const excavatorInventory = useGetApiV1ExcavatorsLots({
    query: { queryKey: getGetApiV1ExcavatorsLotsQueryKey(), staleTime: 0 },
  });
  const amplifierInventory = useGetApiV1FinderAmplifiersLots({
    query: { queryKey: getGetApiV1FinderAmplifiersLotsQueryKey(), staleTime: 0 },
  });
  const enhancers = useGetApiV1Enhancers();
  const finderGroups = Object.values(finderInventory.data ?? {});
  const excavatorGroups = Object.values(excavatorInventory.data ?? {});
  const amplifierGroups = Object.values(amplifierInventory.data ?? {});
  const stock = useQueries({
    queries: (enhancers.data ?? []).map((item) =>
      getGetApiV1LotsItemIdQueryOptions(item.id),
    ),
  });
  const queries = [
    finderInventory,
    excavatorInventory,
    amplifierInventory,
    enhancers,
    ...stock,
  ];
  const equipment: MiningEquipment = {
    finders: finderGroups.flatMap((group) => (group[0] ? [group[0].item] : [])),
    excavators: excavatorGroups.flatMap((group) =>
      group[0] ? [group[0].item] : [],
    ),
    amplifiers: amplifierGroups.flatMap((group) =>
      group[0] ? [group[0].item] : [],
    ),
    enhancers: enhancers.data ?? [],
    lots: [
      ...finderGroups.flat(),
      ...amplifierGroups.flat(),
      ...excavatorGroups.flat(),
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
