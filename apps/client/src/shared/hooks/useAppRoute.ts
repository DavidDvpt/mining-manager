import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import type { AppRouteDefinition } from '@/shared/types/appRoute';
import type { BaseRouteQueries, RouteQueryUpdates } from '@/shared/types/route';
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
): {
  location: import('react-router').Location<any>;
  navigate: import('react-router').NavigateFunction;
  route: import('@/shared/types/appRoute').AppRoute<Prefix, Kind, Action>;
  query: Queries;
  updateQuery: (updates: RouteQueryUpdates<Queries>) => void;
} {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const route = parseAppRoute(location.pathname, definition);
  const query = parseRouteQueries<Queries>(searchParams);

  /** Update only the supplied queries and preserve the current pathname. */
  const updateQuery = (updates: RouteQueryUpdates<Queries>): void => {
    setSearchParams(
      (current): URLSearchParams => {
        Object.entries(updates).forEach(([name, value]): void => {
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
