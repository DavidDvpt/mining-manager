import type { ReactNode } from 'react';

/** Supported catalogue groups displayed by the item store. */
export type ItemStoreKind =
  | 'finder'
  | 'excavator'
  | 'refiner'
  | 'finder-amplifier'
  | 'enhancer'
  | 'material';

/** Normalized catalogue row shared by all item-store column definitions. */
export type ItemStoreRow = {
  id: string;
  name: string;
  kind: ItemStoreKind;
  imageUrl: string | null;
  isRare: boolean | null;
  isUntradeable: boolean | null;
  tt: number | null;
  decay: number | null;
  stock: number | null;
  details: Record<string, unknown>;
};

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
  kind: ItemStoreKind;
  rows: ItemStoreRow[];
  isLoading?: boolean;
  isError?: boolean;
  showMaterialType?: boolean;
  onBuy?: (row: ItemStoreRow) => void;
  onSell?: (row: ItemStoreRow) => void;
};

/** Common shape required from each generated catalogue response. */
export type ItemStoreCatalogueItem = {
  id: string;
  name: string;
  img_id: number | null;
  is_rare: boolean | null;
  is_untradeable: boolean | null;
  economy: { tt: string | null; decay: string | null };
  details: object;
};
