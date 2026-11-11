import type { MouseEventHandler } from 'react';
import { cn } from '../../../lib/utils/styles';
import { Button } from '../../../components/ui/button/button';
import styles from './form-buttons-section.module.scss';

type FormButtonsSectionBaseProps = {
  className?: string;
  submitDisabled?: boolean;
  cancelDisabled?: boolean;
  onCancel?: MouseEventHandler<HTMLButtonElement>;
  cancelLabel?: string;
  submitLabel?: string;
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

/** Render a form action row with an optional cancel button and a submit button. */
export function FormButtonsSection({
  className,
  submitDisabled = false,
  cancelDisabled = false,
  cancelVisible = true,
  fullWidth,
  onCancel,
  cancelLabel = 'Cancel',
  submitLabel = 'Submit',
}: FormButtonsSectionProps) {
  const shouldUseFullWidth = fullWidth === true && cancelVisible === false;

  return (
    <div
      className={cn(
        styles.actions,
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
