import { z } from 'zod';

const envSchema = z.object({
  VITE_API_BASE_URL: z
    .string()
    .optional()
    .refine(
      (value) => !value || value.startsWith('/') || URL.canParse(value),
      'VITE_API_BASE_URL must be a relative path or a valid URL',
    ),
});

const parsedEnv = envSchema.safeParse(import.meta.env);

if (!parsedEnv.success) {
  const errors = parsedEnv.error.issues
    .map((issue) => `${issue.path.join('.') || 'env'}: ${issue.message}`)
    .join('\n');
  throw new Error(`Invalid environment variables:\n${errors}`);
}

export const env = parsedEnv.data;
