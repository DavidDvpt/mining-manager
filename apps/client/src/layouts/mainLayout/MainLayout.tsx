import { Outlet } from 'react-router-dom';

import TopBar from './toolbar/TopBar';
import styles from './main-layout.module.scss';

/** Render the authenticated viewport shell and the active protected route content. */
export function MainLayout(): import('react').JSX.Element {
  return (
    <div className={styles.layout}>
      <TopBar />
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}

export default MainLayout;
