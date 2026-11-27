import * as SelectPrimitive from '@radix-ui/react-select';
import { ChevronDown, ChevronUp } from 'lucide-react';
import type { ComponentPropsWithoutRef, ElementRef } from 'react';
import { forwardRef } from 'react';
import styles from './select.module.scss';

/** Render the Radix select root used by application select controls. */
export const Select = SelectPrimitive.Root;

/** Render the selected value or placeholder inside a select trigger. */
export const SelectValue = SelectPrimitive.Value;

/** Render a styled select trigger with the shared input dimensions. */
export const SelectTrigger = forwardRef<
  ElementRef<typeof SelectPrimitive.Trigger>,
  ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>
>(function SelectTrigger(
  { className, children, ...props },
  ref,
): import('react').JSX.Element {
  return (
    <SelectPrimitive.Trigger
      ref={ref}
      className={[styles.trigger, className].filter(Boolean).join(' ')}
      {...props}
    >
      {children}
      <SelectPrimitive.Icon asChild>
        <ChevronDown className={styles.icon} aria-hidden="true" />
      </SelectPrimitive.Icon>
    </SelectPrimitive.Trigger>
  );
});

/** Render the portalled select options list. */
export const SelectContent = forwardRef<
  ElementRef<typeof SelectPrimitive.Content>,
  ComponentPropsWithoutRef<typeof SelectPrimitive.Content>
>(function SelectContent(
  { className, children, ...props },
  ref,
): import('react').JSX.Element {
  return (
    <SelectPrimitive.Portal>
      <SelectPrimitive.Content
        ref={ref}
        position="popper"
        className={[styles.content, className].filter(Boolean).join(' ')}
        {...props}
      >
        <SelectPrimitive.ScrollUpButton className={styles.scrollButton}>
          <ChevronUp size={16} aria-hidden="true" />
        </SelectPrimitive.ScrollUpButton>
        <SelectPrimitive.Viewport className={styles.viewport}>
          {children}
        </SelectPrimitive.Viewport>
        <SelectPrimitive.ScrollDownButton className={styles.scrollButton}>
          <ChevronDown size={16} aria-hidden="true" />
        </SelectPrimitive.ScrollDownButton>
      </SelectPrimitive.Content>
    </SelectPrimitive.Portal>
  );
});

/** Render one selectable option inside the Radix select list. */
export const SelectItem = forwardRef<
  ElementRef<typeof SelectPrimitive.Item>,
  ComponentPropsWithoutRef<typeof SelectPrimitive.Item> & { rich?: boolean }
>(function SelectItem(
  { className, children, rich, ...props },
  ref,
): import('react').JSX.Element {
  return (
    <SelectPrimitive.Item
      ref={ref}
      className={[styles.item, className].filter(Boolean).join(' ')}
      {...props}
    >
      <SelectPrimitive.ItemText asChild={rich}>
        {rich ? <div>{children}</div> : children}
      </SelectPrimitive.ItemText>
    </SelectPrimitive.Item>
  );
});
