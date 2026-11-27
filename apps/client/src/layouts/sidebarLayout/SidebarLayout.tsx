import type { SidebarLayoutProps } from '@/shared/types/layout';

import styles from './sidebar-layout.module.scss';
import SideNavbar from '@/layouts/sidebarLayout/SideNavbar';

/** Render route-linked sidebar navigation beside the page content. */
export function SidebarLayout({
  buttons,
  sidebarLabel = 'Sidebar navigation',
  children,
}: SidebarLayoutProps): import('react').JSX.Element {
  return (
    <div className={styles.layout}>
      <SideNavbar buttons={buttons} ariaLabel={sidebarLabel} />
      <main className={styles.content}>{children}</main>
    </div>
  );
}

export default SidebarLayout;
