import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';

type QueryContext = Record<string, string | undefined>;
type QueryContextUpdates<T extends QueryContext> = Partial<{
  [Key in keyof T]: T[Key] | null;
}>;

/** Read and update a typed context stored in prefixed URL query parameters. */
export function useQueryContext<T extends QueryContext>(
  parse: (params: URLSearchParams) => T,
) {
  const [searchParams, setSearchParams] = useSearchParams();
  const context = useMemo(() => parse(searchParams), [parse, searchParams]);

  /** Merge context updates into the URL while removing null or undefined values. */
  const updateContext = useCallback(
    (updates: QueryContextUpdates<T>) => {
      setSearchParams(
        (currentParams) => {
          Object.entries(updates).forEach(([key, value]) => {
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
