import { useMemo } from 'react';

import {
  createEnhancerColumns,
  createExcavatorColumns,
  createFinderAmplifierColumns,
  createFinderColumns,
  createMaterialColumns,
  createRefinerColumns,
} from './columns';
import { createBuyColumn, createSummaryColumn } from './columns/common';
import type {
  ItemStoreColumn,
  ItemStoreListProps,
} from '@/shared/types/listItem';
import styles from './item-store-list.module.scss';

/** Render catalogue rows with type-specific columns and flex-based layout. */
export function ItemStoreList({
  kind,
  rows,
  isLoading = false,
  isError = false,
  showMaterialType = false,
  onBuy,
}: ItemStoreListProps) {
  const columns = useMemo<ItemStoreColumn[]>(() => {
    let typeColumns: ItemStoreColumn[] = [];

    switch (kind) {
      case 'finder': typeColumns = createFinderColumns(); break;
      case 'excavator': typeColumns = createExcavatorColumns(); break;
      case 'refiner': typeColumns = createRefinerColumns(); break;
      case 'finder-amplifier': typeColumns = createFinderAmplifierColumns(); break;
      case 'enhancer': typeColumns = createEnhancerColumns(); break;
      case 'material':
        typeColumns = createMaterialColumns({ includeType: showMaterialType });
        break;
    }

    return [
      ...typeColumns,
      createSummaryColumn(),
      createBuyColumn(onBuy),
    ];
  }, [kind, onBuy, showMaterialType]);

  if (isLoading) return <div className={styles.empty}>Loading items…</div>;
  if (isError) return <div className={styles.empty}>Unable to load items.</div>;
  if (rows.length === 0) return <div className={styles.empty}>No items found.</div>;

  return (
    <div className={styles.list} role="table">
      <div className={styles.header} role="row">
        {columns.map((column) => (
          <div
            key={column.key}
            className={styles.cell}
            style={{ flex: column.flex, textAlign: column.align ?? 'left' }}
            role="columnheader"
          >
            {column.label}
          </div>
        ))}
      </div>
      <div className={styles.body}>
        {rows.map((row) => (
          <div key={row.id} className={styles.row} role="row">
            {columns.map((column) => (
              <div
                key={column.key}
                className={`${styles.cell} ${column.key === 'image' ? styles.imageColumn : ''} ${column.kind === 'button' ? styles.actionCell : ''}`}
                style={{ flex: column.flex, textAlign: column.align ?? 'left' }}
                role="cell"
              >
                {column.kind === 'select' ? (
                  <select
                    className={styles.select}
                    value={column.selectValue?.(row) ?? ''}
                    onChange={(event) =>
                      column.onSelectChange?.(row, event.target.value)
                    }
                  >
                    {(column.selectOptions ?? []).map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                ) : column.key === 'image' ? (
                  <div className={styles.imageCell}>{column.render(row)}</div>
                ) : (
                  column.render(row)
                )}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ItemStoreList;
