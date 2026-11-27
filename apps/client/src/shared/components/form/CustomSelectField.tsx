import type { ReactNode } from 'react';
import { useController } from 'react-hook-form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from '@/components/ui/select/select';
import { useSafeFormContext } from './useSafeFormContext';

export type CustomSelectProps = {
  variant: 'custom';
  name: string;
  label: string;
  trigger: ReactNode;
  options: { value: string; label: string; content?: ReactNode }[];
  selection?: 'replace' | 'append';
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  onSelect?: () => void;
};

/** Render React option content with Radix and store a single ID or an ordered list of IDs. */
export function CustomSelectField({
  name,
  label,
  trigger,
  options,
  selection,
  defaultOpen,
  onOpenChange,
  onSelect,
}: CustomSelectProps): import('react').JSX.Element {
  const form = useSafeFormContext();
  const { field, fieldState } = useController({ name, control: form.control });
  const ids: string[] = Array.isArray(field.value) ? field.value : [];
  const currentValue = selection ? ids[0] : field.value;

  /** Store the chosen ID in the configured shape and notify the caller. */
  const selectOption = (id: string): void => {
    if (!id) return;
    if (!selection) field.onChange(id);
    else
      field.onChange(
        selection === 'append' ? [...ids, id] : [id],
        { shouldDirty: true, shouldValidate: true },
      );
    onSelect?.();
  };

  return (
    <Select
      value={selection === 'append' ? '' : (currentValue ?? '')}
      onValueChange={selectOption}
      defaultOpen={defaultOpen}
      onOpenChange={onOpenChange}
      disabled={!options.length}
    >
      <SelectTrigger
        ref={field.ref}
        onBlur={field.onBlur}
        aria-label={label}
        aria-invalid={fieldState.invalid || undefined}
      >
        {trigger}
      </SelectTrigger>
      <SelectContent>
        {options.map(({ value, label, content }) => (
          <SelectItem
            key={value}
            value={value}
            textValue={label}
            rich={content != null}
          >
            {content ?? label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
