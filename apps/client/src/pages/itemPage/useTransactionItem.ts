import { useMemo } from 'react';
import {
  useGetApiV1MaterialsItemId,
  getGetApiV1MaterialsItemIdQueryKey,
  useGetApiV1FindersItemId,
  getGetApiV1FindersItemIdQueryKey,
  useGetApiV1ExcavatorsItemId,
  getGetApiV1ExcavatorsItemIdQueryKey,
  useGetApiV1RefinersItemId,
  getGetApiV1RefinersItemIdQueryKey,
  useGetApiV1FinderAmplifiersItemId,
  getGetApiV1FinderAmplifiersItemIdQueryKey,
  useGetApiV1EnhancersItemId,
  getGetApiV1EnhancersItemIdQueryKey,
} from '@/api/generated/miningManagerAPI';
import { useOutletContext, useParams } from 'react-router-dom';
import type { ItemKind, ItemRow } from '@/shared/types/listItem';
import { toRow } from '@/shared/hooks/useItemStoreData';

/** Resolve the URL item from its domain query; shared query keys reuse cached data on refresh/navigation. */
export function useTransactionItem(): {
  item: ItemRow | null;
  isLoading: boolean;
  isError: boolean;
} {
  const { id = '' } = useParams();
  const { kind } = useOutletContext<{ kind: ItemKind }>();
  const materials = useGetApiV1MaterialsItemId(id, {
    query: {
      queryKey: getGetApiV1MaterialsItemIdQueryKey(id),
      enabled: Boolean(id) && kind === 'material',
    },
  });
  const finders = useGetApiV1FindersItemId(id, {
    query: {
      queryKey: getGetApiV1FindersItemIdQueryKey(id),
      enabled: Boolean(id) && kind === 'finder',
    },
  });
  const excavators = useGetApiV1ExcavatorsItemId(id, {
    query: {
      queryKey: getGetApiV1ExcavatorsItemIdQueryKey(id),
      enabled: Boolean(id) && kind === 'excavator',
    },
  });
  const refiners = useGetApiV1RefinersItemId(id, {
    query: {
      queryKey: getGetApiV1RefinersItemIdQueryKey(id),
      enabled: Boolean(id) && kind === 'refiner',
    },
  });
  const finderAmplifiers = useGetApiV1FinderAmplifiersItemId(id, {
    query: {
      queryKey: getGetApiV1FinderAmplifiersItemIdQueryKey(id),
      enabled: Boolean(id) && kind === 'finder-amplifier',
    },
  });
  const enhancers = useGetApiV1EnhancersItemId(id, {
    query: {
      queryKey: getGetApiV1EnhancersItemIdQueryKey(id),
      enabled: Boolean(id) && kind.includes('enhancer'),
    },
  });
  return useMemo(() => {
    switch (kind) {
      case 'material':
        return {
          item:
            materials.data && materials.data.isActive !== false
              ? toRow(materials.data, kind)
              : null,
          isLoading: materials.isLoading,
          isError: materials.isError,
        };
      case 'finder':
        return {
          item:
            finders.data && finders.data.isActive !== false
              ? toRow(finders.data, kind)
              : null,
          isLoading: finders.isLoading,
          isError: finders.isError,
        };
      case 'excavator':
        return {
          item:
            excavators.data && excavators.data.isActive !== false
              ? toRow(excavators.data, kind)
              : null,
          isLoading: excavators.isLoading,
          isError: excavators.isError,
        };
      case 'refiner':
        return {
          item:
            refiners.data && refiners.data.isActive !== false
              ? toRow(refiners.data, kind)
              : null,
          isLoading: refiners.isLoading,
          isError: refiners.isError,
        };
      case 'finder-amplifier':
        return {
          item:
            finderAmplifiers.data && finderAmplifiers.data.isActive !== false
              ? toRow(finderAmplifiers.data, kind)
              : null,
          isLoading: finderAmplifiers.isLoading,
          isError: finderAmplifiers.isError,
        };
      case 'excavator-enhancer':
      case 'finder-enhancer':
        return {
          item:
            enhancers.data && enhancers.data.isActive !== false
              ? toRow(enhancers.data, kind)
              : null,
          isLoading: enhancers.isLoading,
          isError: enhancers.isError,
        };
    }
  }, [
    kind,
    materials.data,
    materials.isLoading,
    materials.isError,
    finders.data,
    finders.isLoading,
    finders.isError,
    excavators.data,
    excavators.isLoading,
    excavators.isError,
    refiners.data,
    refiners.isLoading,
    refiners.isError,
    finderAmplifiers.data,
    finderAmplifiers.isLoading,
    finderAmplifiers.isError,
    enhancers.data,
    enhancers.isLoading,
    enhancers.isError,
  ]);
}
