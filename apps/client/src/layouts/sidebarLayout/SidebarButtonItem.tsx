import { useState, type ButtonHTMLAttributes } from 'react';

import { Button } from '@/components/ui/button/button';
import { AppIconName } from '@/shared/components/icon';
import type {
  SidebarButtonItemProps,
  SidebarButton,
} from '@/shared/types/layout';

import { useSidebarLayoutContext } from './SidebarLayoutContext';
import styles from './sidebar-layout.module.scss';

/** Render one sidebar button and its optional nested choices. */
export function SidebarButtonItem({ button, level }: SidebarButtonItemProps) {
  const { activeButtonId, selectButton } = useSidebarLayoutContext();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const hasChildren = Boolean(button.children?.length);
  const isActive = activeButtonId === button.id;
  const isChildActive = button.children?.some(
    (child: SidebarButton) => child.id === activeButtonId,
  );
  const isExpanded = Boolean((isActive || isChildActive) && !isCollapsed);

  const buttonProps: ButtonHTMLAttributes<HTMLButtonElement> = {
    type: 'button',
    disabled: button.disabled,
    'aria-current': isActive ? 'page' : undefined,
    'aria-expanded': hasChildren ? isExpanded : undefined,
    onClick: () => {
      if (hasChildren && isExpanded) {
        setIsCollapsed(true);
        return;
      }

      setIsCollapsed(false);
      selectButton(button.id);
    },
  };

  return (
    <div className={styles.item} data-level={level}>
      <Button
        {...buttonProps}
        icon={hasChildren ? AppIconName.ChevronDown : button.icon}
        iconClassName={
          hasChildren && !isExpanded ? styles.collapsedChevron : undefined
        }
        iconPosition="end"
        size="small"
        variant={isExpanded ? 'sidebar-active' : 'sidebar-default'}
      >
        <span>{button.label}</span>
      </Button>
      {hasChildren && isExpanded ? (
        <div className={styles.submenu}>
          {button.children?.map((child) => (
            <SidebarButtonItem
              key={child.id}
              button={child}
              level={level + 1}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}
