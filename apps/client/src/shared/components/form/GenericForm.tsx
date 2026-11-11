import { zodResolver } from '@hookform/resolvers/zod';
import { FormProvider, useForm } from 'react-hook-form';
import type { DefaultValues, FieldValues } from 'react-hook-form';
import type { ZodType } from 'zod';
import { cn } from '../../../lib/utils/styles';
import type { GenericFormProps } from './form.types';

/** Provide a typed React Hook Form context backed by a Zod schema. */
export function GenericForm<
  TInput extends FieldValues,
  TOutput extends FieldValues = TInput,
>({
  schema,
  defaultValues,
  onSubmit,
  children,
  className,
}: GenericFormProps<TInput, TOutput> & { schema: ZodType<TOutput, TInput> }) {
  const methods = useForm<TInput, unknown, TOutput>({
    resolver: zodResolver(schema),
    defaultValues: defaultValues as DefaultValues<TInput>,
  });

  return (
    <FormProvider {...methods}>
      <form className={cn(className)} onSubmit={methods.handleSubmit(onSubmit)}>
        {children}
      </form>
    </FormProvider>
  );
}
