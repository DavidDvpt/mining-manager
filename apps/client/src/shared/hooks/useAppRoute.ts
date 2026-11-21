import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import type { AppRouteDefinition } from '@/shared/types/appRoute';
import type {
  BaseRouteQueries,
  RouteQueryUpdates,
} from '@/shared/types/route';
import {
  parseAppRoute,
  parseRouteQueries,
  routeQueryKeyToSnakeCase,
} from '@/shared/utils/route';

/** Read and update typed queries while exposing the shared route operations. */
export function useAppRoute<
  Prefix extends string,
  Kind extends string,
  Action extends string,
  Queries extends BaseRouteQueries,
>(
  definition: AppRouteDefinition<Prefix, Kind, Action>,
) {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const route = parseAppRoute(location.pathname, definition);
  const query = parseRouteQueries<Queries>(searchParams);

  /** Update only the supplied queries and preserve the current pathname. */
  const updateQuery = (updates: RouteQueryUpdates<Queries>) => {
    setSearchParams(
      (current) => {
        Object.entries(updates).forEach(([name, value]) => {
          const queryName = routeQueryKeyToSnakeCase(name);
          if (value === undefined || value === null || value === '') {
            current.delete(queryName);
          } else {
            current.set(queryName, String(value));
          }
        });
        return current;
      },
      { replace: true },
    );
  };

  return { location, navigate, route, query, updateQuery };
}
