import type { PropsWithChildren } from 'react';
import type { AppIconName } from '@/shared/components/icon';

/** A sidebar button that can contain nested choices. */
export type SidebarButtonId = string;

export type SidebarButton<Id extends SidebarButtonId = SidebarButtonId> = {
  id: Id;
  label: string;
  icon?: AppIconName;
  children?: SidebarButton<Id>[];
  disabled?: boolean;
  separatorBefore?: boolean;
  separatorAfter?: boolean;
  highlighted?: boolean;
};

/** State and actions exposed by a sidebar layout context. */
export type SidebarLayoutContextValue = {
  activeButtonId: string;
  selectButton: (buttonId: string) => void;
};

/** Public properties accepted by the sidebar layout component. */
export type SidebarLayoutProps = PropsWithChildren<{
  buttons: SidebarButton[];
  defaultButtonId?: string;
  onButtonChange?: (buttonId: string) => void;
  sidebarLabel?: string;
}>;

/** Internal properties used to render a sidebar button and its nested level. */
export type SidebarButtonItemProps = {
  button: SidebarButton;
  level: number;
};
