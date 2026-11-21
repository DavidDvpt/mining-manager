/** Describe the allowed values for a page's typed route segments. */
export type AppRouteDefinition<
  Prefix extends string,
  Kind extends string,
  Action extends string,
> = {
  prefix: Prefix;
  kinds: readonly Kind[];
  actions?: readonly Action[];
};

/** Represent the normalized segments shared by every application page. */
export type AppRoute<
  Prefix extends string,
  Kind extends string,
  Action extends string,
> = {
  prefix?: Prefix;
  kind?: Kind;
  id?: string;
  action?: Action;
};

export type RouteQueryValue = string | undefined;
