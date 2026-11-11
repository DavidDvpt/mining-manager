import type { ReactNode } from 'react';
import type { FieldValues, Path, SubmitHandler } from 'react-hook-form';
import type { ZodType } from 'zod';

export type FormFieldError<TValues extends FieldValues> = {
  key: Path<TValues>;
  message: string;
};

export type GenericFormProps<
  TInput extends FieldValues,
  TOutput extends FieldValues = TInput,
> = {
  schema: ZodType<TOutput, TInput>;
  defaultValues: TInput;
  onSubmit: SubmitHandler<TOutput>;
  children: ReactNode;
  className?: string;
  externalError?: string | null;
};
