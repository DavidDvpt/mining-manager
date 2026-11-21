import { useMemo } from 'react';

import {
  useGetApiV1ExcavatorsStock,
  useGetApiV1Enhancers,
  useGetApiV1Excavators,
  useGetApiV1FinderAmplifiers,
  useGetApiV1FinderAmplifiersStock,
  useGetApiV1Finders,
  useGetApiV1FindersStock,
  useGetApiV1Materials,
  useGetApiV1Refiners,
  useGetApiV1RefinersStock,
  useGetApiV1StorageMaterialStock,
} from '@/api/generated/miningManagerAPI';
import { getItemImageUrl } from '@/config/images';
import { parseNumber } from '@/shared/utils';
import type {
  ItemDetailsByKind,
  ItemCatalogueItem,
  ItemKind,
  ItemRow,
  ItemRowFor,
} from '@/shared/types/listItem';

/** Normalize one OpenAPI catalogue response into the row shape used by the flex list. */
const toRow = <K extends ItemKind>(
  item: ItemCatalogueItem<ItemDetailsByKind[K]>,
  kind: K,
  stock: number | null = null,
): ItemRowFor<K> => ({
  id: item.id,
  name: item.name,
  kind,
  imageUrl: getItemImageUrl(item.imgId ?? null),
  isRare: item.isRare,
  isUntradeable: item.isUntradeable,
  tt: parseNumber(item.economy.tt),
  decay: parseNumber(item.economy.decay),
  stock,
  details: item.details as ItemRowFor<K>['details'],
});

/** Load every catalogue group and expose normalized rows for the transaction store views. */
export function useItemStoreData(): {
  rows: Record<ItemKind, ItemRow[]>;
  isLoading: boolean;
  isError: boolean;
} {
  const finders = useGetApiV1Finders();
  const excavators = useGetApiV1Excavators();
  const refiners = useGetApiV1Refiners();
  const finderAmplifiers = useGetApiV1FinderAmplifiers();
  const enhancers = useGetApiV1Enhancers();
  const materials = useGetApiV1Materials();
  const materialStock = useGetApiV1StorageMaterialStock();
  const finderStock = useGetApiV1FindersStock();
  const excavatorStock = useGetApiV1ExcavatorsStock();
  const refinerStock = useGetApiV1RefinersStock();
  const finderAmplifierStock = useGetApiV1FinderAmplifiersStock();

  const rows: Record<ItemKind, ItemRow[]> = useMemo(
    (): {
      finder: ItemRowFor<'finder'>[];
      excavator: ItemRowFor<'excavator'>[];
      refiner: ItemRowFor<'refiner'>[];
      'finder-amplifier': ItemRowFor<'finder-amplifier'>[];
      'finder-enhancer': ItemRowFor<'finder-enhancer'>[];
      'excavator-enhancer': ItemRowFor<'excavator-enhancer'>[];
      material: ItemRowFor<'material'>[];
    } => ({
      finder: (finders.data ?? []).map((item): ItemRowFor<'finder'> =>
        toRow(item, 'finder', finderStock.data?.[item.id] ?? 0),
      ),
      excavator: (excavators.data ?? []).map((item): ItemRowFor<'excavator'> =>
        toRow(item, 'excavator', excavatorStock.data?.[item.id] ?? 0),
      ),
      refiner: (refiners.data ?? []).map((item): ItemRowFor<'refiner'> =>
        toRow(item, 'refiner', refinerStock.data?.[item.id] ?? 0),
      ),
      'finder-amplifier': (finderAmplifiers.data ?? []).map(
        (item): ItemRowFor<'finder-amplifier'> =>
          toRow(
            item,
            'finder-amplifier',
            finderAmplifierStock.data?.[item.id] ?? 0,
          ),
      ),
      'finder-enhancer': (enhancers.data ?? [])
        .filter((f) => f.details.tool === 'FINDER')
        .map((item): ItemRowFor<'finder-enhancer'> =>
          toRow(item, 'finder-enhancer'),
        ),
      'excavator-enhancer': (enhancers.data ?? [])
        .filter((f) => f.details.tool === 'EXCAVATOR')
        .map((item): ItemRowFor<'excavator-enhancer'> =>
          toRow(item, 'excavator-enhancer'),
        ),
      material: (materials.data ?? []).map((item): ItemRowFor<'material'> =>
        toRow(item, 'material', materialStock.data?.[item.id] ?? 0),
      ),
    }),
    [
      finders.data,
      excavators.data,
      refiners.data,
      finderAmplifiers.data,
      enhancers.data,
      materials.data,
      materialStock.data,
      finderStock.data,
      excavatorStock.data,
      refinerStock.data,
      finderAmplifierStock.data,
    ],
  );

  return {
    rows,
    isLoading: [
      finders,
      excavators,
      refiners,
      finderAmplifiers,
      enhancers,
      materials,
      materialStock,
      finderStock,
      excavatorStock,
      refinerStock,
      finderAmplifierStock,
    ].some((query): boolean => query.isLoading),
    isError: [
      finders,
      excavators,
      refiners,
      finderAmplifiers,
      enhancers,
      materials,
      materialStock,
      finderStock,
      excavatorStock,
      refinerStock,
      finderAmplifierStock,
    ].some((query): boolean => query.isError),
  };
}
