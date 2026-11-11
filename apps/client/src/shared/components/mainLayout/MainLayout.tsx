import type { PropsWithChildren } from 'react';
import TopBar from './toolbar/TopBar';
import styles from './main-layout.module.scss';

/** Render the fixed viewport shell with a header and independently scrollable main content. */
export function MainLayout({ children }: PropsWithChildren) {
  return (
    <div className={styles.layout}>
      <TopBar />
      <main className={styles.main}>{children}</main>
    </div>
  );
}

export default MainLayout;
