import { Button } from '@/components/ui/button/button';
import type { AppIconName as AppIconNameType } from '@/shared/components/icon';
import { Tooltip } from '@/shared/components/tooltip';

/** Create a reusable fixed-width icon action column for any table row shape. */
export const createIconColumn = <TRow extends object>({
  key,
  icon,
  variant,
  ariaLabel,
  title,
  className,
  isVisible,
  onClick,
}: {
  key: string;
  icon: AppIconNameType;
  variant: 'primary' | 'ternary';
  ariaLabel: string;
  title: string;
  className?: string;
  isVisible?: (row: TRow) => boolean;
  onClick?: (row: TRow) => void;
}): {
  key: string;
  label: string;
  kind: 'button';
  flex: string;
  align: 'center';
  render: (row: TRow) => import('react').JSX.Element;
} => ({
  key,
  label: '',
  kind: 'button' as const,
  flex: '0 0 2.75rem',
  align: 'center' as const,
  render: (row: TRow): import('react').JSX.Element => {
    const visible = isVisible?.(row) ?? true;

    const button = (
      <Button
        type="button"
        variant={variant}
        size="small"
        className={className}
        icon={icon}
        iconOnly
        aria-label={ariaLabel}
        tabIndex={visible ? undefined : -1}
        aria-hidden={!visible}
        style={{ visibility: visible ? 'visible' : 'hidden' }}
        onClick={(): void => {
          if (visible) onClick?.(row);
        }}
      />
    );

    return visible ? <Tooltip content={title}>{button}</Tooltip> : button;
  },
});
