import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  getGetApiV1MeQueryKey,
  usePostApiV1Signin,
} from '../../api/generated/miningManagerAPI';
import { useTranslations } from '../../i18n/useTranslations';
import { ApiError } from '../../lib/axios/types';
import { SignInForm } from './SignInForm';
import type { SignInValues } from './signInSchema';
import styles from './sign-in-page.module.scss';

/** Render the public signin page and establish the HttpOnly cookie session. */
export function SignInPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const signIn = usePostApiV1Signin();
  const apiError = signIn.error instanceof ApiError ? signIn.error : null;
  const { t } = useTranslations();

  const handleSubmit = async (values: SignInValues): Promise<void> => {
    await signIn.mutateAsync({ data: values });
    await queryClient.invalidateQueries({ queryKey: getGetApiV1MeQueryKey() });
    navigate('/', { replace: true });
  };

  return (
    <main className={styles.page}>
      <section className={styles.panel} aria-labelledby="signin-title">
        <h1 id="signin-title">{t('AUTH.SIGNIN.TITLE')}</h1>
        <p className={styles.subtitle}>{t('AUTH.SIGNIN.SUBTITLE')}</p>
        <SignInForm
          error={apiError}
          isSubmitting={signIn.isPending}
          onSubmit={handleSubmit}
        />
      </section>
    </main>
  );
}

export default SignInPage;
