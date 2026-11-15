import * as RadioGroupPrimitive from '@radix-ui/react-radio-group';
import type { ComponentPropsWithoutRef, ElementRef } from 'react';
import { forwardRef } from 'react';

import styles from './radio-group.module.scss';

/** Render a shared Radix radio-group container. */
export const RadioGroup = RadioGroupPrimitive.Root;

/** Render a shared Radix radio item with the application radio indicator. */
export const RadioGroupItem = forwardRef<
  ElementRef<typeof RadioGroupPrimitive.Item>,
  ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Item>
>(function RadioGroupItem({ className, children, ...props }, ref) {
  return (
    <RadioGroupPrimitive.Item
      ref={ref}
      className={[styles.item, className].filter(Boolean).join(' ')}
      {...props}
    >
      <RadioGroupPrimitive.Indicator className={styles.indicator} />
      {children}
    </RadioGroupPrimitive.Item>
  );
});

RadioGroupItem.displayName = RadioGroupPrimitive.Item.displayName;
