import SidebarButton from '@/layouts/sidebarLayout/SidebarButton';
import styles from './sidebar-layout.module.scss';
import { SidebarButtonType } from '@/shared';
import { matchPath, useLocation } from 'react-router-dom';

interface SideNavbarProps {
  buttons: SidebarButtonType<string>[];
  ariaLabel: string;
}

function SideNavbar({ buttons, ariaLabel }: SideNavbarProps) {
  const location = useLocation();
  const pathname = location.pathname;

  function isRouteActive(linkTo: string, pathname: string) {
    return Boolean(matchPath({ path: linkTo, end: false }, pathname));
  }
  return (
    <aside className={styles.sidebar} aria-label={ariaLabel}>
      <nav className={styles.navigation}>
        {buttons.map((button) => {
          return (
            <SidebarButton
              key={button.linkTo}
              button={button}
              level={0}
              isActive={isRouteActive(button.linkTo, pathname)}
              isExpanded={
                Boolean(button.children?.length) &&
                button.linkTo.startsWith(pathname)
              }
            />
          );
        })}
      </nav>
    </aside>
  );
}

export default SideNavbar;
