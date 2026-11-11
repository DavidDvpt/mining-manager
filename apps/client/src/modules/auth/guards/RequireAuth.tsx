import { Navigate, Outlet } from 'react-router-dom';
import { useGetApiV1Me } from '../../../api/generated/miningManagerAPI';
import { useTranslations } from '../../../i18n/useTranslations';

/** Protect application routes with the current HttpOnly cookie session. */
export function RequireAuth() {
  const currentUser = useGetApiV1Me();
  const { t } = useTranslations();

  if (currentUser.isPending) {
    return <p>{t('AUTH.SESSION.LOADING')}</p>;
  }

  if (!currentUser.data) {
    return <Navigate to="/signin" replace />;
  }

  return <Outlet />;
}
