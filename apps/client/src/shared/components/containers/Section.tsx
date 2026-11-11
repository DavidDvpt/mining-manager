import type { ContainerProps } from './container.types';
import styles from './containers.module.scss';

/** Render a styled content block intended to group a home feature. */
export function Section({ className, children, ...props }: ContainerProps) {
  return (
    <section
      className={[styles.section, className].filter(Boolean).join(' ')}
      {...props}
    >
      {children}
    </section>
  );
}

export default Section;
