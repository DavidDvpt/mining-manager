import type { ComponentProps } from 'react';
import { cn } from '../../../lib/utils/styles';
import styles from './input.module.scss';

/** Render the base input control used by form-specific field components. */
export function Input({ className, ...props }: ComponentProps<'input'>) {
  return <input className={cn(styles.input, className)} {...props} />;
}
