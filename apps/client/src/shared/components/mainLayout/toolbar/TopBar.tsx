import { Link } from 'react-router-dom';
import brand from '../../../../assets/images/brand.png';
import styles from './toolbar.module.scss';

/** Render the persistent application header and its home navigation link. */
export function TopBar() {
  return (
    <header className={styles.topBar}>
      <Link className={styles.brand} to="/" aria-label="Accueil Mining Manager">
        <img src={brand} alt="Mining Manager" />
      </Link>
    </header>
  );
}

export default TopBar;
