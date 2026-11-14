import * as CheckboxPrimitive from '@radix-ui/react-checkbox';
import type { ComponentPropsWithoutRef, ComponentRef } from 'react';
import { forwardRef } from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils/styles';
import styles from './checkbox.module.scss';

/** Render the shared accessible checkbox primitive. */
export const Checkbox = forwardRef<ComponentRef<typeof CheckboxPrimitive.Root>, ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root>>(
  ({ className, ...props }, ref) => (
    <CheckboxPrimitive.Root ref={ref} className={cn(styles.checkbox, className)} {...props}>
      <CheckboxPrimitive.Indicator className={styles.indicator}><Check size={14} strokeWidth={3} /></CheckboxPrimitive.Indicator>
    </CheckboxPrimitive.Root>
  ),
);

Checkbox.displayName = CheckboxPrimitive.Root.displayName;
