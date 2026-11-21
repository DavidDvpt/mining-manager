import { NavLink } from 'react-router-dom';

import brand from '@/assets/images/brand.png';
import { useTranslations } from '@/i18n/useTranslations';
import ProfileMenu from './ProfileMenu';
import LanguageSelector from './LanguageSelector';
import TopBarNav from './TopBarNav';
import styles from './toolbar.module.scss';

/** Render the persistent application header and its primary navigation links. */
export function TopBar(): import('react').JSX.Element {
  const { t } = useTranslations();

  return (
    <header className={styles.topBar}>
      <NavLink className={styles.brand} to="/" aria-label={t('APP.HOME_LINK')}>
        <img src={brand} alt="Mining Manager" />
      </NavLink>
      <TopBarNav />
      <div className={styles.toolbarActions}>
        <LanguageSelector />
        <ProfileMenu />
      </div>
    </header>
  );
}

export default TopBar;
