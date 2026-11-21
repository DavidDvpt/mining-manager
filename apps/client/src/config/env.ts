import { z } from 'zod';

const envSchema = z.object({
  VITE_API_BASE_URL: z
    .string()
    .optional()
    .refine(
      (value): boolean =>
        !value || value.startsWith('/') || URL.canParse(value),
      'VITE_API_BASE_URL must be a relative path or a valid URL',
    ),
  VITE_IMAGE_BASE_URL: z
    .string()
    .refine(
      (value): boolean =>
        !value || value.startsWith('/') || URL.canParse(value),
      'VITE_IMAGE_BASE_URL must be a relative path or a valid URL',
    )
    .default(''),
});

const parsedEnv = envSchema.safeParse(import.meta.env);

if (!parsedEnv.success) {
  const errors = parsedEnv.error.issues
    .map(
      (issue): string => `${issue.path.join('.') || 'env'}: ${issue.message}`,
    )
    .join('\n');
  throw new Error(`Invalid environment variables:\n${errors}`);
}

export const env = parsedEnv.data;
