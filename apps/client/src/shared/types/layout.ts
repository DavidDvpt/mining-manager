import type { PropsWithChildren } from 'react';
import type { AppIconName } from '@/shared/components/icon';

/** A sidebar button that can contain nested choices. */
export type SidebarButtonId = string;

export type SidebarButtonType<Id extends SidebarButtonId = SidebarButtonId> = {
  id: Id;
  label: string;
  linkTo: string;
  icon?: AppIconName;
  children?: SidebarButtonType<Id>[];
  disabled?: boolean;
  separatorBefore?: boolean;
  separatorAfter?: boolean;
  highlighted?: boolean;
};

/** Public properties accepted by the sidebar layout component. */
export type SidebarLayoutProps = PropsWithChildren<{
  buttons: SidebarButtonType[];
  sidebarLabel?: string;
}>;

/** Internal properties used to render a sidebar button and its nested level. */
export type SidebarButtonItemProps = {
  button: SidebarButtonType;
  level: number;
  pathname: string;
};
