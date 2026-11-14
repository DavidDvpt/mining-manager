import { Button } from '@/components/ui/button/button';
import type { AppIconName as AppIconNameType } from '@/shared/components/icon';

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
}) => ({
  key,
  label: '',
  kind: 'button' as const,
  flex: '0 0 2.75rem',
  align: 'center' as const,
  render: (row: TRow) => {
    const visible = isVisible?.(row) ?? true;

    return (
      <Button
        type="button"
        variant={variant}
        size="small"
        className={className}
        icon={icon}
        iconOnly
        aria-label={ariaLabel}
        title={visible ? title : undefined}
        tabIndex={visible ? undefined : -1}
        aria-hidden={!visible}
        style={{ visibility: visible ? 'visible' : 'hidden' }}
        onClick={() => {
          if (visible) onClick?.(row);
        }}
      />
    );
  },
});
