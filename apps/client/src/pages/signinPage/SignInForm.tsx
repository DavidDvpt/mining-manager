import type { ApiError } from '../../lib/axios/types';
import { useTranslations } from '../../i18n/useTranslations';
import { FormButtonsSection } from '../../shared/components/form/FormButtonsSection';
import { GenericForm } from '../../shared/components/form/GenericForm';
import { InputRHF } from '../../shared/components/form/InputRHF';
import { createSignInSchema, type SignInValues } from './signInSchema';
import styles from './sign-in-form.module.scss';

type SignInFormProps = {
  error: ApiError | null;
  isSubmitting: boolean;
  onSubmit: (values: SignInValues) => void | Promise<void>;
};

/** Render and validate the public cookie-based signin form. */
export function SignInForm({ error, isSubmitting, onSubmit }: SignInFormProps) {
  const { t } = useTranslations();

  return (
    <GenericForm
      schema={createSignInSchema(t)}
      defaultValues={{ pseudo: '', password: '' }}
      onSubmit={onSubmit}
      className={styles.form}
    >
      <InputRHF
        name="pseudo"
        label={t('AUTH.SIGNIN.PSEUDO')}
        type="text"
        autoComplete="username"
      />
      <InputRHF
        name="password"
        label={t('AUTH.SIGNIN.PASSWORD')}
        type="password"
        autoComplete="current-password"
      />
      {error ? (
        <p className={styles.formError} role="alert">
          {error.message}
        </p>
      ) : null}
      <FormButtonsSection
        cancelVisible={false}
        fullWidth
        submitDisabled={isSubmitting}
        submitLabel={
          isSubmitting ? t('AUTH.SIGNIN.SUBMITTING') : t('AUTH.SIGNIN.SUBMIT')
        }
      />
    </GenericForm>
  );
}
