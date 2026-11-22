import { useEffect } from 'react';
import { useFormContext } from 'react-hook-form';
import { Checkbox } from '@/components/ui/checkbox';
import { cn } from '@/lib/utils/styles';
import styles from './checkbox-rhf.module.scss';

type CheckboxRHFProps = {
  name: string;
  label?: string;
  checkedValue?: string;
  checked?: boolean;
  bindToForm?: boolean;
  disabled?: boolean;
  wrapperClassName?: string;
  labelClassName?: string;
  onCheckedChange?: (checked: boolean) => void;
};

/** Bind or control a checkbox while optionally excluding it from form state. */
export function CheckboxRHF({
  name,
  label,
  checkedValue,
  checked,
  bindToForm = true,
  disabled = false,
  wrapperClassName,
  labelClassName,
  onCheckedChange,
}: CheckboxRHFProps): import('react').JSX.Element {
  const form = useFormContext();

  useEffect((): void => {
    if (bindToForm) form.register(name);
  }, [bindToForm, form, name]);

  const fieldValue = form.watch(name);
  const formValue =
    bindToForm && checkedValue
      ? Array.isArray(fieldValue) && fieldValue.includes(checkedValue)
      : bindToForm
        ? Boolean(fieldValue)
        : false;
  const value = checked ?? formValue;

  /** Store the checkbox value in RHF and notify the consumer of the new state. */
  const handleCheckedChange = (checked: boolean): void => {
    const nextChecked = checked === true;
    const nextValue = checkedValue
      ? ((): any[] => {
          const currentValues = Array.isArray(fieldValue) ? fieldValue : [];
          return nextChecked
            ? [...currentValues, checkedValue]
            : currentValues.filter(
                (currentValue): boolean => currentValue !== checkedValue,
              );
        })()
      : nextChecked;
    if (bindToForm) {
      form.setValue(name, nextValue, {
        shouldDirty: true,
        shouldTouch: true,
        shouldValidate: true,
      });
    }
    onCheckedChange?.(nextChecked);
  };

  const id = checkedValue ? `${name}-${checkedValue}` : name;
  return (
    <div className={cn(styles.wrapper, wrapperClassName)}>
      <Checkbox
        id={id}
        checked={value}
        disabled={disabled}
        onCheckedChange={handleCheckedChange}
      />
      {label ? (
        <label htmlFor={id} className={cn(styles.label, labelClassName)}>
          {label}
        </label>
      ) : null}
    </div>
  );
}

export default CheckboxRHF;
