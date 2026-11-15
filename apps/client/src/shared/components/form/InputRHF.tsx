import type { InputHTMLAttributes, ReactNode } from 'react';
import { useState } from 'react';
import { Input } from '@/components/ui/input/input';
import { useTranslations } from '@/i18n/useTranslations';
import { Label } from '@/components/ui/label/label';
import { cn } from '@/lib/utils/styles';
import { AppIcon, AppIconName } from '@/shared/components/icon';
import { useSafeFormContext } from './useSafeFormContext';
import styles from './input-rhf.module.scss';

type InputRHFProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'name'> & {
  name: string;
  label: ReactNode;
};

/** Bind a styled input and its accessible validation message to React Hook Form. */
export function InputRHF({ name, label, className, id, ...props }: InputRHFProps) {
  const form = useSafeFormContext();
  const { t } = useTranslations();
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const fieldState = form.getFieldState(name, form.formState);
  const inputId = id ?? name;
  const isPasswordField = props.type === 'password';
  const inputType =
    isPasswordField && isPasswordVisible ? 'text' : props.type;
  const registration = form.register(name, {
    valueAsNumber: props.type === 'number',
  });

  return (
    <div className={styles.field}>
      <Label htmlFor={inputId}>{label}</Label>
      <div className={styles.control}>
        <Input
          {...registration}
          {...props}
          id={inputId}
          type={inputType}
          aria-invalid={fieldState.invalid || undefined}
          aria-describedby={fieldState.error ? `${inputId}-error` : undefined}
          className={cn(
            fieldState.error && styles.invalid,
            isPasswordField && styles.passwordInput,
            props.readOnly && styles.readOnly,
            className,
          )}
        />
        {isPasswordField ? (
          <button
            type="button"
            className={styles.passwordToggle}
            onClick={() => setIsPasswordVisible((visible) => !visible)}
            aria-label={
              isPasswordVisible
                ? t('AUTH.SIGNIN.HIDE_PASSWORD')
                : t('AUTH.SIGNIN.SHOW_PASSWORD')
            }
            aria-pressed={isPasswordVisible}
          >
            <AppIcon
              name={isPasswordVisible ? AppIconName.EyeOff : AppIconName.Eye}
              size={16}
            />
          </button>
        ) : null}
      </div>
      {fieldState.error?.message ? (
        <p id={`${inputId}-error`} className={styles.error} role="alert">
          {String(fieldState.error.message)}
        </p>
      ) : null}
    </div>
  );
}
