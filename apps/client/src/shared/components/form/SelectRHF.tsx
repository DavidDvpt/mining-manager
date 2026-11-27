import type { SelectHTMLAttributes } from 'react';
import { Label } from '@/components/ui/label/label';
import { CustomSelectField, type CustomSelectProps } from './CustomSelectField';
import { useSafeFormContext } from './useSafeFormContext';
import styles from './select-rhf.module.scss';

type NativeSelectProps = Omit<
  SelectHTMLAttributes<HTMLSelectElement>,
  'name'
> & {
  variant?: never;
  name: string;
  label: string;
  inline?: boolean;
  options: Array<{ value: string; label: string }>;
};

/** Bind a native select or custom option list to RHF, with optional inline labeling for native selects. */
export function SelectRHF(
  props: NativeSelectProps | CustomSelectProps,
): import('react').JSX.Element {
  const form = useSafeFormContext();
  if (props.variant === 'custom') return <CustomSelectField {...props} />;
  const { name, label, options, className, id, inline, ...nativeProps } = props;
  const fieldState = form.getFieldState(name, form.formState);
  const selectId = id ?? name;

  return (
    <div className={inline ? `${styles.field} ${styles.inline}` : styles.field}>
      <Label htmlFor={selectId}>{label}</Label>
      <select
        {...form.register(name)}
        {...nativeProps}
        id={selectId}
        aria-invalid={fieldState.invalid || undefined}
        aria-describedby={fieldState.error ? `${selectId}-error` : undefined}
        className={[
          styles.select,
          className,
          fieldState.error && styles.invalid,
        ]
          .filter(Boolean)
          .join(' ')}
      >
        {options.map((option): import('react').JSX.Element => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {fieldState.error?.message ? (
        <p id={`${selectId}-error`} className={styles.error} role="alert">
          {String(fieldState.error.message)}
        </p>
      ) : null}
    </div>
  );
}

export default SelectRHF;
