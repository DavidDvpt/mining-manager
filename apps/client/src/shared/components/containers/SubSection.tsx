import type { ContainerProps } from './container.types';
import styles from './containers.module.scss';

/** Render a neutral wrapper for content nested inside a Section. */
export function SubSection({ className, children, ...props }: ContainerProps) {
  return (
    <div
      className={[styles.subSection, className].filter(Boolean).join(' ')}
      {...props}
    >
      {children}
    </div>
  );
}

export default SubSection;
