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
  ItemStoreCatalogueItem,
  ItemStoreKind,
  ItemStoreRow,
} from '@/shared/types/listItem';

/** Normalize one OpenAPI catalogue response into the row shape used by the flex list. */
const toStoreRow = (
  item: ItemStoreCatalogueItem,
  kind: ItemStoreKind,
  stock: number | null = null,
): ItemStoreRow => ({
  id: item.id,
  name: item.name,
  kind,
  imageUrl: getItemImageUrl(item.img_id),
  isRare: item.is_rare,
  isUntradeable: item.is_untradeable,
  tt: parseNumber(item.economy.tt),
  decay: parseNumber(item.economy.decay),
  stock,
  details: item.details as Record<string, unknown>,
});

/** Load every catalogue group and expose normalized rows for the transaction store views. */
export function useItemStoreData() {
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

  const rows = useMemo(
    () => ({
      finder: (finders.data ?? []).map((item) =>
        toStoreRow(item, 'finder', finderStock.data?.[item.id] ?? 0),
      ),
      excavator: (excavators.data ?? []).map((item) =>
        toStoreRow(item, 'excavator', excavatorStock.data?.[item.id] ?? 0),
      ),
      refiner: (refiners.data ?? []).map((item) =>
        toStoreRow(item, 'refiner', refinerStock.data?.[item.id] ?? 0),
      ),
      'finder-amplifier': (finderAmplifiers.data ?? []).map((item) =>
        toStoreRow(item, 'finder-amplifier', finderAmplifierStock.data?.[item.id] ?? 0),
      ),
      enhancer: (enhancers.data ?? []).map((item) =>
        toStoreRow(item, 'enhancer'),
      ),
      material: (materials.data ?? []).map((item) =>
        toStoreRow(item, 'material', materialStock.data?.[item.id] ?? 0),
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
    ].some((query) => query.isLoading),
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
    ].some((query) => query.isError),
  };
}
