import { NavLink } from 'react-router-dom';

import { buttonVariants } from '@/components/ui/button/button.variants';
import { useTranslations } from '@/i18n/useTranslations';
import { cn } from '@/lib/utils/styles';
import styles from './toolbar.module.scss';

const toolbarLinks = [
  { label: 'Items', route: '/items' },
  { label: 'Mining', route: '/mining' },
  { label: 'Storage', route: '/storage' },
] as const;

/** Render the primary navigation links displayed in the top bar. */
export function TopBarNav(): import('react').JSX.Element {
  const { t } = useTranslations();

  return (
    <nav className={styles.navigation} aria-label={t('APP.PRIMARY_NAVIGATION')}>
      {toolbarLinks.map(({ label, route }): import('react').JSX.Element => (
        <NavLink
          key={route}
          to={route}
          className={({ isActive }): string =>
            cn(
              buttonVariants({ variant: 'topbar' }),
              styles.navButton,
              isActive && styles.activeLink,
            )
          }
        >
          {label}
        </NavLink>
      ))}
    </nav>
  );
}

export default TopBarNav;
