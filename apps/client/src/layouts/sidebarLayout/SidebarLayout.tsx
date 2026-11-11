import { useCallback, useMemo, useState } from 'react';

import { SidebarButtonItem } from './SidebarButtonItem';
import { SidebarLayoutContext } from './SidebarLayoutContext';
import type { SidebarLayoutProps } from '@/shared/types/layout';

import styles from './sidebar-layout.module.scss';

/**
 * Provide sidebar selection state to a page and render its two-column shell.
 * The first button is selected by default unless `defaultButtonId` is supplied.
 */
export function SidebarLayout({
  buttons,
  defaultButtonId,
  onButtonChange,
  sidebarLabel = 'Sidebar navigation',
  children,
}: SidebarLayoutProps) {
  const firstButtonId = buttons[0]?.id ?? '';
  const [activeButtonId, setActiveButtonId] = useState(
    defaultButtonId ?? firstButtonId,
  );

  /** Update the selected sidebar button and notify the owning page. */
  const selectButton = useCallback((buttonId: string) => {
    setActiveButtonId(buttonId);
    onButtonChange?.(buttonId);
  }, [onButtonChange]);

  const contextValue = useMemo(
    () => ({ activeButtonId, selectButton }),
    [activeButtonId, selectButton],
  );

  return (
    <SidebarLayoutContext.Provider value={contextValue}>
      <div className={styles.layout}>
        <aside className={styles.sidebar} aria-label={sidebarLabel}>
          <nav className={styles.navigation}>
            {buttons.map((button) => (
              <SidebarButtonItem
                key={button.id}
                button={button}
                level={0}
              />
            ))}
          </nav>
        </aside>
        <main className={styles.content}>{children}</main>
      </div>
    </SidebarLayoutContext.Provider>
  );
}

export default SidebarLayout;
