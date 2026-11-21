import type { SidebarButtonItemProps } from '@/shared/types/layout';

import styles from './sidebar-layout.module.scss';
import { matchPath, NavLink } from 'react-router-dom';
import { useState } from 'react';

/** Render a navigation link with active/highlighted styling and any nested choices. */
function SidebarButton({
  button,
  level,
  pathname,
}: SidebarButtonItemProps): import('react').JSX.Element {
  const [expanded, setExpanded] = useState(false);
  const hasChildren = Boolean(button.children?.length);

  function isRouteActive(linkTo: string, pathname: string): boolean {
    return Boolean(matchPath({ path: linkTo, end: true }, pathname));
  }

  const handleClick = () => (level === 0 ? setExpanded(!expanded) : undefined);

  const isActive = isRouteActive(button.linkTo, pathname);

  return (
    <>
      {button.separatorBefore ? (
        <div className={styles.separator} role="separator" />
      ) : null}
      <div className={styles.item}>
        <NavLink
          to={button.linkTo}
          onClick={handleClick}
          className={[
            styles.link,
            isActive ? styles.active : undefined,
            button.highlighted ? styles.highlighted : undefined,
          ]
            .filter(Boolean)
            .join(' ')}
        >
          <span className={styles.label}>{button.label}</span>
        </NavLink>
        {hasChildren && expanded ? (
          <div className={styles.submenu}>
            {button.children?.map((child): import('react').JSX.Element => (
              <SidebarButton
                key={child.linkTo}
                button={child}
                level={level + 1}
                pathname={pathname}
              />
            ))}
          </div>
        ) : null}
      </div>
      {button.separatorAfter ? (
        <div className={styles.separator} role="separator" />
      ) : null}
    </>
  );
}

export default SidebarButton;
