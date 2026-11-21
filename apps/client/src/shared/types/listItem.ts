import { ItemKind } from '@/router/constants';
import type { EnhancerDetailsResponse } from '@/api/generated/model/enhancerDetailsResponse';
import type { ExcavatorDetailsResponse } from '@/api/generated/model/excavatorDetailsResponse';
import type { FinderAmplifierDetailsResponse } from '@/api/generated/model/finderAmplifierDetailsResponse';
import type { FinderDetailsResponse } from '@/api/generated/model/finderDetailsResponse';
import type { MaterialDetailsResponse } from '@/api/generated/model/materialDetailsResponse';
import type { RefinerDetailsResponse } from '@/api/generated/model/refinerDetailsResponse';
import type { ReactNode } from 'react';

/** Supported catalogue groups displayed by the item store. */
export type ItemStoreKind =
  | 'finder'
  | 'excavator'
  | 'refiner'
  | 'finder-amplifier'
  | 'enhancer'
  | 'material';

/** Maps each store kind to the detail shape returned by its catalogue endpoint. */
export type ItemStoreDetailsByKind = {
  finder: FinderDetailsResponse;
  excavator: ExcavatorDetailsResponse;
  refiner: RefinerDetailsResponse;
  'finder-amplifier': FinderAmplifierDetailsResponse;
  enhancer: EnhancerDetailsResponse;
  material: MaterialDetailsResponse;
};

type ItemStoreRowDetails<K extends ItemStoreKind> =
  ItemStoreDetailsByKind[K] & Record<string, any>;

/** Normalized catalogue row shared by all item-store column definitions. */
type ItemStoreRowBase = {
  id: string;
  name: string;
  imageUrl: string | null;
  isRare: boolean | null;
  isUntradeable: boolean | null;
  tt: number | null;
  decay: number | null;
  stock: number | null;
};

/** A store row whose details are tied to its discriminating store kind. */
export type ItemStoreRowFor<K extends ItemStoreKind> = ItemStoreRowBase & {
  kind: K;
  details: ItemStoreRowDetails<K>;
};

/** Union of all normalized item-store rows, discriminated by `kind`. */
export type ItemStoreRow = {
  [K in ItemStoreKind]: ItemStoreRowFor<K>;
}[ItemStoreKind];

/** Declarative definition for one flex-list column. */
export type ItemStoreColumn<TRow extends object = ItemStoreRow> = {
  key: string;
  label: string;
  kind?: 'text' | 'select' | 'button';
  flex?: string;
  align?: 'left' | 'center' | 'right';
  cellClassName?: string;
  render: (row: TRow) => ReactNode;
  selectOptions?: Array<{ label: string; value: string }>;
  selectValue?: (row: TRow) => string;
  onSelectChange?: (row: TRow, value: string) => void;
  onClick?: (row: TRow) => void;
};

/** Props accepted by the normalized item-store list component. */
export type ItemStoreListProps = {
  kind: ItemKind;
  rows: ItemStoreRow[];
  isLoading?: boolean;
  isError?: boolean;
  showMaterialType?: boolean;
  onBuy?: (row: ItemStoreRow) => void;
  onSell?: (row: ItemStoreRow) => void;
  onEdit?: (row: ItemStoreRow) => void;
};

/** Common shape required from each generated catalogue response. */
export type ItemStoreCatalogueItem<
  TDetails extends ItemStoreDetailsByKind[ItemStoreKind] =
    ItemStoreDetailsByKind[ItemStoreKind],
> = {
  id: string;
  name: string;
  img_id: number | null;
  is_rare: boolean | null;
  is_untradeable: boolean | null;
  economy: { tt: string | null; decay: string | null };
  details: TDetails;
};
