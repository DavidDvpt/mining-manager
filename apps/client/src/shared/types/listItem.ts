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
  tt: string | null;
  decay: string | null;
  details: Record<string, unknown>;
};

/** Declarative definition for one flex-list column. */
export type ItemStoreColumn = {
  key: string;
  label: string;
  kind?: 'text' | 'select' | 'button';
  flex?: string;
  align?: 'left' | 'center' | 'right';
  render: (row: ItemStoreRow) => ReactNode;
  selectOptions?: Array<{ label: string; value: string }>;
  selectValue?: (row: ItemStoreRow) => string;
  onSelectChange?: (row: ItemStoreRow, value: string) => void;
  onClick?: (row: ItemStoreRow) => void;
};

/** Props accepted by the normalized item-store list component. */
export type ItemStoreListProps = {
  kind: ItemStoreKind;
  rows: ItemStoreRow[];
  isLoading?: boolean;
  isError?: boolean;
  showMaterialType?: boolean;
  onBuy?: (row: ItemStoreRow) => void;
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
