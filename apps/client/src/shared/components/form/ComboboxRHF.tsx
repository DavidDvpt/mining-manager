import type { InputHTMLAttributes, ReactNode } from 'react';
import { useController } from 'react-hook-form';

import { Input } from '@/components/ui/input/input';
import { Label } from '@/components/ui/label/label';
import { cn } from '@/lib/utils/styles';

import { useSafeFormContext } from './useSafeFormContext';
import styles from './combobox-rhf.module.scss';

/** Describe one existing option displayed by the combobox. */
export type ComboboxOption = {
  value: string;
  label: string;
};

type ComboboxRHFProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'name'> & {
  name: string;
  label: ReactNode;
  options: ComboboxOption[];
};

/** Bind a free-text combobox with existing options to the current RHF form. */
export function ComboboxRHF({
  name,
  label,
  options,
  className,
  id,
  ...props
}: ComboboxRHFProps): import('react').JSX.Element {
  useSafeFormContext();
  const { field, fieldState } = useController({ name });
  const inputId = id ?? name;
  const listId = `${inputId}-options`;
  const fieldValue = String(field.value ?? '');
  const displayedValue =
    options.find((option): boolean => option.value === fieldValue)?.label ??
    fieldValue;

  /** Store an option value when selected, or preserve a new free-text value. */
  const handleChange = (value: string): void => {
    const selectedOption = options.find(
      (option): boolean => option.label === value,
    );
    field.onChange(selectedOption?.value ?? value);
  };

  return (
    <div className={styles.field}>
      <Label htmlFor={inputId}>{label}</Label>
      <Input
        {...props}
        id={inputId}
        name={field.name}
        ref={field.ref}
        value={displayedValue}
        list={listId}
        aria-invalid={fieldState.invalid || undefined}
        aria-describedby={fieldState.error ? `${inputId}-error` : undefined}
        className={cn(fieldState.error && styles.invalid, className)}
        onChange={(event): void => handleChange(event.target.value)}
        onBlur={field.onBlur}
      />
      <datalist id={listId}>
        {options.map((option): import('react').JSX.Element => (
          <option key={option.value} value={option.label} />
        ))}
      </datalist>
      {fieldState.error?.message ? (
        <p id={`${inputId}-error`} className={styles.error} role="alert">
          {String(fieldState.error.message)}
        </p>
      ) : null}
    </div>
  );
}

export default ComboboxRHF;
