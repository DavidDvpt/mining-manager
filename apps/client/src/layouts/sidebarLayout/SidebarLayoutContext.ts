import { createContext, useContext } from 'react';

import type { SidebarLayoutContextValue } from '@/shared/types/layout';

/** React context carrying the active sidebar selection and its update action. */
export const SidebarLayoutContext = createContext<
  SidebarLayoutContextValue | undefined
>(undefined);

/** Read the active sidebar selection from a descendant of `SidebarLayout`. */
export function useSidebarLayoutContext(): SidebarLayoutContextValue {
  const context = useContext(SidebarLayoutContext);

  if (!context) {
    throw new Error(
      'useSidebarLayoutContext must be used inside SidebarLayout',
    );
  }

  return context;
}
