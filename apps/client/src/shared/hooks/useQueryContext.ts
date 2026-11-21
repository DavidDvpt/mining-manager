import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';

type QueryContext = Record<string, unknown>;
type QueryContextUpdates<T extends QueryContext> = Partial<{
  [Key in keyof T]: T[Key] | null;
}>;

/** Read and update a typed context stored in prefixed URL query parameters. */
export function useQueryContext<T extends QueryContext>(
  parse: (params: URLSearchParams) => T,
): { context: T; updateContext: (updates: QueryContextUpdates<T>) => void } {
  const [searchParams, setSearchParams] = useSearchParams();
  const context = useMemo((): T => parse(searchParams), [parse, searchParams]);

  /** Merge context updates into the URL while removing null or undefined values. */
  const updateContext = useCallback(
    (updates: QueryContextUpdates<T>): void => {
      setSearchParams(
        (currentParams): URLSearchParams => {
          Object.entries(updates).forEach(([key, value]): void => {
            const parameter = `context_${key}`;
            if (value === null || value === undefined || value === '') {
              currentParams.delete(parameter);
            } else {
              currentParams.set(parameter, String(value));
            }
          });
          return currentParams;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  return { context, updateContext };
}
