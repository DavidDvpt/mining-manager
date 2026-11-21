import type { MouseEventHandler } from 'react';
import { cn } from '@/lib/utils/styles';
import { Button } from '@/components/ui/button/button';
import styles from './form-buttons-section.module.scss';

type FormButtonsSectionBaseProps = {
  className?: string;
  submitDisabled?: boolean;
  cancelDisabled?: boolean;
  onCancel?: MouseEventHandler<HTMLButtonElement>;
  cancelLabel?: string;
  submitLabel?: string;
  align?: 'center' | 'right';
};

type SingleButtonProps = {
  cancelVisible: false;
  fullWidth?: boolean;
};

type TwoButtonProps = {
  cancelVisible?: true;
  fullWidth?: never;
};

type FormButtonsSectionProps = FormButtonsSectionBaseProps &
  (SingleButtonProps | TwoButtonProps);

/** Render a form action row with optional cancellation and configurable alignment. */
export function FormButtonsSection({
  className,
  submitDisabled = false,
  cancelDisabled = false,
  cancelVisible = true,
  fullWidth,
  onCancel,
  cancelLabel = 'Cancel',
  submitLabel = 'Submit',
  align = 'center',
}: FormButtonsSectionProps): import('react').JSX.Element {
  const shouldUseFullWidth = fullWidth === true && cancelVisible === false;

  return (
    <div
      className={cn(
        styles.actions,
        align === 'right' && styles.alignRight,
        shouldUseFullWidth && styles.fullWidth,
        className,
      )}
    >
      {cancelVisible ? (
        <Button
          type="reset"
          variant="ternary"
          size="default"
          onClick={onCancel}
          disabled={cancelDisabled}
          className={styles.button}
        >
          {cancelLabel}
        </Button>
      ) : null}
      <Button
        type="submit"
        variant="primary"
        size="default"
        disabled={submitDisabled}
        className={styles.button}
      >
        {submitLabel}
      </Button>
    </div>
  );
}

export default FormButtonsSection;
