import type { ChangeEvent } from 'react';
import type { ItemStoreColumn } from '@/shared/types/listItem';
import { TooltipProvider } from '@/shared/components/tooltip';
import styles from './app-list.module.scss';

export type AppListProps<TRow extends { id: string }> = {
  columns: ItemStoreColumn<TRow>[];
  rows: TRow[];
  isLoading?: boolean;
  isError?: boolean;
  loadingMessage?: string;
  errorMessage?: string;
  emptyMessage?: string;
};

/** Render a generic flex table from row data and declarative column definitions. */
export function AppList<TRow extends { id: string }>({
  columns,
  rows,
  isLoading = false,
  isError = false,
  loadingMessage = 'Loading…',
  errorMessage = 'Unable to load data.',
  emptyMessage = 'No data found.',
}: AppListProps<TRow>): import('react').JSX.Element {
  if (isLoading) return <div className={styles.empty}>{loadingMessage}</div>;
  if (isError) return <div className={styles.empty}>{errorMessage}</div>;
  if (rows.length === 0)
    return <div className={styles.empty}>{emptyMessage}</div>;

  /** Forward a select cell change to the column's row-specific callback. */
  const handleSelectChange = (
    column: ItemStoreColumn<TRow>,
    row: TRow,
    event: ChangeEvent<HTMLSelectElement>,
  ): void | undefined => column.onSelectChange?.(row, event.target.value);

  return (
    <TooltipProvider>
      <div className={styles.list} role="table">
        <div className={styles.header} role="row">
          {columns.map((column): import('react').JSX.Element => (
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
          {rows.map((row): import('react').JSX.Element => (
            <div key={row.id} className={styles.row} role="row">
              {columns.map((column): import('react').JSX.Element => (
                <div
                  key={column.key}
                  className={`${styles.cell} ${column.cellClassName ?? ''} ${column.kind === 'button' ? styles.actionCell : ''}`}
                  style={{
                    flex: column.flex,
                    textAlign: column.align ?? 'left',
                  }}
                  role="cell"
                >
                  {column.kind === 'select' ? (
                    <select
                      className={styles.select}
                      value={column.selectValue?.(row) ?? ''}
                      onChange={(event): void | undefined =>
                        handleSelectChange(column, row, event)
                      }
                    >
                      {(column.selectOptions ?? []).map(
                        (option): import('react').JSX.Element => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ),
                      )}
                    </select>
                  ) : (
                    column.render(row)
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </TooltipProvider>
  );
}

export default AppList;
