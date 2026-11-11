import { Navigate, Outlet } from 'react-router-dom';
import { useGetApiV1Me } from '../../../api/generated/miningManagerAPI';
import { useTranslations } from '../../../i18n/useTranslations';

/** Allow public pages only while no valid cookie session exists. */
export function GuestOnly() {
  const currentUser = useGetApiV1Me();
  const { t } = useTranslations();

  if (currentUser.isPending) {
    return <p>{t('AUTH.SESSION.CHECKING')}</p>;
  }

  if (currentUser.data) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
