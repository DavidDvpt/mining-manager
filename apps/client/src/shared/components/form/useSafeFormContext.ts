import { useFormContext } from 'react-hook-form';
import type { FieldValues, UseFormReturn } from 'react-hook-form';

/** Return the current form context and fail clearly when used outside a form. */
export function useSafeFormContext<TValues extends FieldValues>(): UseFormReturn<TValues> {
  const context = useFormContext<TValues>();

  if (!context) {
    throw new Error(
      'useSafeFormContext must be used inside a GenericForm component.',
    );
  }

  return context;
}
