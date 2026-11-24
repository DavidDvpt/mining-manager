import type { ReactNode } from 'react';
import { useController } from 'react-hook-form';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { useSafeFormContext } from './useSafeFormContext';

type RadioRHFProps = {
  name: string;
  children: ReactNode;
  className?: string;
  'aria-label'?: string;
};

type RadioRHFItemProps = {
  value: string;
  children: ReactNode;
  className?: string;
};

/** Bind a Radix radio group to one field in the shared form context. */
export function RadioRHF({
  name,
  children,
  className,
  'aria-label': ariaLabel,
}: RadioRHFProps): import('react').JSX.Element {
  const form = useSafeFormContext();
  const { field } = useController({ name, control: form.control });
  return (
    <RadioGroup
      name={field.name}
      value={field.value ?? ''}
      onValueChange={field.onChange}
      onBlur={field.onBlur}
      className={className}
      aria-label={ariaLabel}
    >
      {children}
    </RadioGroup>
  );
}

/** Render a labeled choice inside a RadioRHF group. */
export function RadioRHFItem({
  value,
  children,
  className,
}: RadioRHFItemProps): import('react').JSX.Element {
  return (
    <label className={className}>
      <RadioGroupItem value={value} />
      {children}
    </label>
  );
}
