import type { ContainerProps } from './container.types';
import styles from './containers.module.scss';

/** Render the page-level wrapper that fills the available application area. */
export function Panel({ className, children, ...props }: ContainerProps) {
  return (
    <div className={[styles.panel, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
}

export default Panel;
