/** Queries shared by every application page that opens a URL-driven modal. */
export interface BaseRouteQueries {
  modal?: string;
  modalContext?: string;
}

/** Transaction-specific queries extending the application-wide route queries. */
export interface TransactionRouteQueries extends BaseRouteQueries {
  ownedOnly?: 'true' | 'false';
  type?: string;
}

/** Describe partial query updates accepted by a typed route hook. */
export type RouteQueryUpdates<Queries extends BaseRouteQueries> =
  Partial<{ [Key in keyof Queries]: Queries[Key] | null }>;
