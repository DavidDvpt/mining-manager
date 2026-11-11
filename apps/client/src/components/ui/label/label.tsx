import * as LabelPrimitive from '@radix-ui/react-label';
import type { ComponentPropsWithoutRef } from 'react';
import { cn } from '../../../lib/utils/styles';
import styles from './label.module.scss';

/** Render an accessible Radix label with the shared form styling. */
export function Label({
  className,
  ...props
}: ComponentPropsWithoutRef<typeof LabelPrimitive.Root>) {
  return (
    <LabelPrimitive.Root
      className={cn(styles.label, className)}
      {...props}
    />
  );
}
