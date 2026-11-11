import { useMemo } from 'react';

import {
  useGetApiV1Enhancers,
  useGetApiV1Excavators,
  useGetApiV1FinderAmplifiers,
  useGetApiV1Finders,
  useGetApiV1Materials,
  useGetApiV1Refiners,
} from '@/api/generated/miningManagerAPI';
import { getItemImageUrl } from '@/config/images';
import type {
  ItemStoreCatalogueItem,
  ItemStoreKind,
  ItemStoreRow,
} from '@/shared/types/listItem';

/** Normalize one OpenAPI catalogue response into the row shape used by the flex list. */
const toStoreRow = (
  item: ItemStoreCatalogueItem,
  kind: ItemStoreKind,
): ItemStoreRow => ({
  id: item.id,
  name: item.name,
  kind,
  imageUrl: getItemImageUrl(item.img_id),
  isRare: item.is_rare,
  isUntradeable: item.is_untradeable,
  tt: item.economy.tt,
  decay: item.economy.decay,
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

  const rows = useMemo(
    () => ({
      finder: (finders.data ?? []).map((item) => toStoreRow(item, 'finder')),
      excavator: (excavators.data ?? []).map((item) =>
        toStoreRow(item, 'excavator'),
      ),
      refiner: (refiners.data ?? []).map((item) => toStoreRow(item, 'refiner')),
      'finder-amplifier': (finderAmplifiers.data ?? []).map((item) =>
        toStoreRow(item, 'finder-amplifier'),
      ),
      enhancer: (enhancers.data ?? []).map((item) =>
        toStoreRow(item, 'enhancer'),
      ),
      material: (materials.data ?? []).map((item) =>
        toStoreRow(item, 'material'),
      ),
    }),
    [
      finders.data,
      excavators.data,
      refiners.data,
      finderAmplifiers.data,
      enhancers.data,
      materials.data,
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
    ].some((query) => query.isLoading),
    isError: [
      finders,
      excavators,
      refiners,
      finderAmplifiers,
      enhancers,
      materials,
    ].some((query) => query.isError),
  };
}
