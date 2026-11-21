import type { SelectHTMLAttributes } from 'react';

import { Label } from '@/components/ui/label/label';

import { useSafeFormContext } from './useSafeFormContext';
import styles from './select-rhf.module.scss';

type SelectRHFProps = Omit<SelectHTMLAttributes<HTMLSelectElement>, 'name'> & {
  name: string;
  label: string;
  options: Array<{ value: string; label: string }>;
};

/** Bind a native select and its validation message to the current RHF form. */
export function SelectRHF({
  name,
  label,
  options,
  className,
  id,
  ...props
}: SelectRHFProps): import('react').JSX.Element {
  const form = useSafeFormContext();
  const fieldState = form.getFieldState(name, form.formState);
  const selectId = id ?? name;

  return (
    <div className={styles.field}>
      <Label htmlFor={selectId}>{label}</Label>
      <select
        {...form.register(name)}
        {...props}
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
