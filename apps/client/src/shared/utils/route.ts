import type { AppRoute, AppRouteDefinition } from '@/shared/types/appRoute';
import type { BaseRouteQueries } from '@/shared/types/route';

/** Convert a snake_case query key from the URL to camelCase. */
export function routeQueryKeyToCamelCase(key: string): string {
  return key.replace(/_([a-z])/g, (_, character: string): string =>
    character.toUpperCase(),
  );
}

/** Convert a camelCase query key to snake_case for the URL. */
export function routeQueryKeyToSnakeCase(key: string): string {
  return key.replace(
    /[A-Z]/g,
    (character): string => `_${character.toLowerCase()}`,
  );
}

/** Parse URL query parameters into a typed camelCase query object. */
export function parseRouteQueries<Queries extends BaseRouteQueries>(
  searchParams: URLSearchParams,
): Queries {
  return Object.fromEntries(
    Array.from(searchParams.entries()).map(([key, value]): [string, string] => [
      routeQueryKeyToCamelCase(key),
      value,
    ]),
  ) as unknown as Queries;
}

/** Parse a JSON-encoded query value without allowing malformed URL data to throw. */
export function parseQueryValue<T>(value?: string): T | undefined {
  if (!value) return undefined;

  try {
    return JSON.parse(value) as T;
  } catch {
    return undefined;
  }
}

/** Decode a URL segment without allowing malformed user-controlled URLs to throw. */
function decodeRouteSegment(segment: string): string {
  try {
    return decodeURIComponent(segment);
  } catch {
    return segment;
  }
}

/** Parse a pathname into validated generic route segments. */
export function parseAppRoute<
  Prefix extends string,
  Kind extends string,
  Action extends string,
>(
  pathname: string,
  definition: AppRouteDefinition<Prefix, Kind, Action>,
): AppRoute<Prefix, Kind, Action> {
  const segments = pathname.split('/').filter(Boolean).map(decodeRouteSegment);
  const [prefix, kind, id, action] = segments;
  const hasPrefix = prefix === definition.prefix;
  const isKind = hasPrefix && definition.kinds.includes(kind as Kind);
  const isAction =
    isKind && (definition.actions?.includes(action as Action) ?? false);

  return {
    prefix: hasPrefix ? definition.prefix : undefined,
    kind: isKind ? (kind as Kind) : undefined,
    id: isKind ? id : undefined,
    action: isAction ? (action as Action) : undefined,
  };
}

/** Build a route from its typed segments, omitting absent trailing segments. */
export function buildAppRoute<
  Prefix extends string,
  Kind extends string,
  Action extends string,
>(
  route: AppRoute<Prefix, Kind, Action> & { prefix: Prefix; kind: Kind },
): string {
  return `/${[route.prefix, route.kind, route.id, route.action]
    .filter((segment): segment is string => Boolean(segment))
    .map(encodeURIComponent)
    .join('/')}`;
}
