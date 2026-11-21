import type { SidebarButtonItemProps } from '@/shared/types/layout';

import styles from './sidebar-layout.module.scss';
import { NavLink, useNavigate } from 'react-router-dom';

/** Render one sidebar button with optional separators, highlighting, and nested choices. */
function SidebarButton({
  button,
  level,
  isActive,
  isExpanded,
}: SidebarButtonItemProps): import('react').JSX.Element {
  const navigate = useNavigate();

  const hasChildren = Boolean(button.children?.length);

  // const buttonProps: ButtonHTMLAttributes<HTMLButtonElement> = {
  //   type: 'button',
  //   disabled: button.disabled,
  //   'aria-current': isActive ? 'page' : undefined,
  //   'aria-expanded': hasChildren ? isExpanded : undefined,
  //   onClick: () => {
  //     console.log(button.linkTo);
  //     navigate(button.linkTo);
  //   },
  // };

  return (
    <>
      {button.separatorBefore ? (
        <div className={styles.separator} role="separator" />
      ) : null}
      <div className={styles.item}>
        <NavLink
          to={button.linkTo}
          // {...buttonProps}
          // icon={hasChildren ? AppIconName.ChevronDown : button.icon}
          // iconClassName={
          //   hasChildren && !isExpanded ? styles.collapsedChevron : undefined
          // }
          // iconPosition="end"
          // size="small"
          className={button.highlighted ? styles.highlighted : undefined}
          // variant={isExpanded ? 'sidebar-active' : 'sidebar-default'}
        >
          <span className={styles.label}>{button.label}</span>
        </NavLink>
        {hasChildren && isExpanded ? (
          <div className={styles.submenu}>
            {button.children?.map((child): import('react').JSX.Element => (
              <SidebarButton
                key={child.linkTo}
                button={child}
                level={level + 1}
                isActive
                isExpanded={false}
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
