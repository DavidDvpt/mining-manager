import { useEffect } from 'react';
import { useFormContext } from 'react-hook-form';
import { Checkbox } from '@/components/ui/checkbox';
import { cn } from '@/lib/utils/styles';
import styles from './checkbox-rhf.module.scss';

type CheckboxRHFProps = {
  name: string;
  label?: string;
  checkedValue?: string;
  disabled?: boolean;
  wrapperClassName?: string;
  labelClassName?: string;
  onCheckedChange?: (checked: boolean) => void;
};

/** Bind the shared checkbox primitive to the current React Hook Form context. */
export function CheckboxRHF({
  name,
  label,
  checkedValue,
  disabled = false,
  wrapperClassName,
  labelClassName,
  onCheckedChange,
}: CheckboxRHFProps) {
  const form = useFormContext();

  useEffect(() => {
    form.register(name);
  }, [form, name]);

  const fieldValue = form.watch(name);
  const value = checkedValue
    ? Array.isArray(fieldValue) && fieldValue.includes(checkedValue)
    : Boolean(fieldValue);

  /** Store the checkbox value in RHF and notify the consumer of the new state. */
  const handleCheckedChange = (checked: boolean) => {
    const nextChecked = checked === true;
    const nextValue = checkedValue
      ? (() => {
          const currentValues = Array.isArray(fieldValue) ? fieldValue : [];
          return nextChecked
            ? [...currentValues, checkedValue]
            : currentValues.filter(
                (currentValue) => currentValue !== checkedValue,
              );
        })()
      : nextChecked;
    form.setValue(name, nextValue, {
      shouldDirty: true,
      shouldTouch: true,
      shouldValidate: true,
    });
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
