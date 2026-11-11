import { Slot } from '@radix-ui/react-slot';
import type { VariantProps } from 'class-variance-authority';
import type { ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/utils/styles';
import { AppIcon, type AppIconName } from '@/shared/components/icon';
import { buttonVariants } from './button.variants';
import styles from './button.module.scss';

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
    icon?: AppIconName;
    iconClassName?: string;
    iconOnly?: boolean;
    iconPosition?: 'start' | 'end';
  };

/** Render a styled button with optional leading, trailing, or icon-only content. */
export function Button({
  className,
  variant,
  size,
  asChild = false,
  icon,
  iconClassName,
  iconOnly = false,
  iconPosition = 'start',
  children,
  ...props
}: ButtonProps) {
  const Component = asChild ? Slot : 'button';
  /** Wrap a decorative icon with the spacing and alignment required by the button. */
  const renderIcon = (position: 'start' | 'end') =>
    icon ? (
      <span
        className={cn(styles.icon, iconClassName)}
        data-position={position}
        aria-hidden="true"
      >
        <AppIcon name={icon} size={16} />
      </span>
    ) : null;

  return (
    <Component
      className={cn(
        buttonVariants({ variant, size }),
        iconOnly && styles.iconOnly,
        className,
      )}
      {...props}
    >
      {iconPosition === 'start' ? renderIcon('start') : null}
      {children}
      {iconPosition === 'end' ? renderIcon('end') : null}
    </Component>
  );
}
