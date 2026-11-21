import type { EnhancerDetailsResponse } from '@/api/generated/model/enhancerDetailsResponse';
import type { ExcavatorDetailsResponse } from '@/api/generated/model/excavatorDetailsResponse';
import type { FinderAmplifierDetailsResponse } from '@/api/generated/model/finderAmplifierDetailsResponse';
import type { FinderDetailsResponse } from '@/api/generated/model/finderDetailsResponse';
import type { MaterialDetailsResponse } from '@/api/generated/model/materialDetailsResponse';
import type { RefinerDetailsResponse } from '@/api/generated/model/refinerDetailsResponse';
import type { ReactNode } from 'react';

/** Supported catalogue groups displayed by the item store. */
export type ItemKind =
  | 'finder'
  | 'excavator'
  | 'refiner'
  | 'finder-amplifier'
  | 'finder-enhancer'
  | 'excavator-enhancer'
  | 'material';

/** Maps each store kind to the detail shape returned by its catalogue endpoint. */
export type ItemDetailsByKind = {
  finder: FinderDetailsResponse;
  excavator: ExcavatorDetailsResponse;
  refiner: RefinerDetailsResponse;
  'finder-amplifier': FinderAmplifierDetailsResponse;
  'finder-enhancer': EnhancerDetailsResponse;
  'excavator-enhancer': EnhancerDetailsResponse;
  material: MaterialDetailsResponse;
};

type ItemRowDetails<K extends ItemKind> = ItemDetailsByKind[K] &
  Record<string, any>;

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
export type ItemRowFor<K extends ItemKind> = ItemStoreRowBase & {
  kind: K;
  details: ItemRowDetails<K>;
};

/** Union of all normalized item-store rows, discriminated by `kind`. */
export type ItemRow = {
  [K in ItemKind]: ItemRowFor<K>;
}[ItemKind];

/** Declarative definition for one flex-list column. */
export type ItemColumn<TRow extends object = ItemRow> = {
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
export type IItemListProps = {
  kind: ItemKind;
  rows: ItemRow[];
  isLoading?: boolean;
  isError?: boolean;
  showMaterialType?: boolean;
  onBuy?: (row: ItemRow) => void;
  onSell?: (row: ItemRow) => void;
  onEdit?: (row: ItemRow) => void;
};

/** Common shape required from each generated catalogue response. */
export type ItemCatalogueItem<
  TDetails extends ItemDetailsByKind[ItemKind] = ItemDetailsByKind[ItemKind],
> = {
  id: string;
  name: string;
  imgId: number | null;
  isRare: boolean | null;
  isUntradeable: boolean | null;
  economy: { tt: string | null; decay: string | null };
  details: TDetails;
};
