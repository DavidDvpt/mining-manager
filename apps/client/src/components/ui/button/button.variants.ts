import { cva } from 'class-variance-authority';
import styles from './button.module.scss';

/** Define the supported button visual and sizing variants. */
export const buttonVariants = cva(styles.button, {
  variants: {
    variant: {
      primary: styles.primary,
      ternary: styles.ternary,
    },
    size: {
      default: styles.default,
      small: styles.small,
    },
  },
  defaultVariants: {
    variant: 'primary',
    size: 'default',
  },
});
