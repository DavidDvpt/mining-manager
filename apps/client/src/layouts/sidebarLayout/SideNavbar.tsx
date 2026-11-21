import SidebarButton from '@/layouts/sidebarLayout/SidebarButton';
import styles from './sidebar-layout.module.scss';
import { SidebarButtonType } from '@/shared';
import { useLocation } from 'react-router-dom';

interface SideNavbarProps {
  buttons: SidebarButtonType<string>[];
  ariaLabel: string;
}

function SideNavbar({
  buttons,
  ariaLabel,
}: SideNavbarProps): import('react').JSX.Element {
  const location = useLocation();
  const pathname = location.pathname;

  return (
    <aside className={styles.sidebar} aria-label={ariaLabel}>
      <nav className={styles.navigation}>
        {buttons.map((button): import('react').JSX.Element => {
          return (
            <SidebarButton
              key={button.linkTo}
              button={button}
              level={0}
              pathname={pathname}
            />
          );
        })}
      </nav>
    </aside>
  );
}

export default SideNavbar;
