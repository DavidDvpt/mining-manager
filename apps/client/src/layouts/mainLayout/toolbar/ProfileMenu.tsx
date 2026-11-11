import { useQueryClient } from '@tanstack/react-query';
import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import {
  getGetApiV1MeQueryKey,
  useGetApiV1Me,
  usePostApiV1Logout,
} from '@/api/generated/miningManagerAPI';
import { AppIcon, AppIconName } from '@/shared/components/icon';
import { useTranslations } from '@/i18n/useTranslations';
import { useDismissOnOutsideInteraction } from '@/shared/hooks/useDismissOnOutsideInteraction';
import styles from './profile.module.scss';

/** Render the authenticated user's profile trigger and actions menu. */
export function ProfileMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const currentUser = useGetApiV1Me();
  const logout = usePostApiV1Logout();
  const { t } = useTranslations();
  const pseudo = currentUser.data?.pseudo?.trim() ?? '';
  const avatarLetter = (pseudo[0] ?? 'U').toUpperCase();

  useDismissOnOutsideInteraction(menuRef, () => setIsOpen(false), isOpen);

  const handleProfile = () => {
    setIsOpen(false);
    navigate('/profile');
  };

  const handleLogout = async () => {
    /**
     * Log out through the API and navigate only after success.
     * Cancel and seed the current-user query to prevent GuestOnly from
     * refetching `/me` after the authentication cookies are deleted.
     */
    setIsOpen(false);
    const currentUserQueryKey = getGetApiV1MeQueryKey();
    await queryClient.cancelQueries({ queryKey: currentUserQueryKey });

    try {
      await logout.mutateAsync();
    } catch {
      return;
    }

    queryClient.setQueryDefaults(currentUserQueryKey, { staleTime: Infinity });
    queryClient.setQueryData(currentUserQueryKey, null);
    navigate('/signin', { replace: true });
  };

  return (
    <div ref={menuRef} className={styles.profileMenu}>
      <button
        type="button"
        className={styles.profileTrigger}
        aria-label={t('APP.PROFILE_MENU')}
        aria-expanded={isOpen}
        onClick={() => setIsOpen((open) => !open)}
      >
        <span className={styles.avatar} aria-hidden="true">
          {avatarLetter}
        </span>
        <AppIcon name={AppIconName.ChevronDown} size={16} aria-hidden="true" />
      </button>
      {isOpen ? (
        <div className={styles.profileDropdown} role="menu">
          <button
            type="button"
            className={styles.profileAction}
            role="menuitem"
            onClick={handleProfile}
          >
            {t('APP.PROFILE')}
          </button>
          <button
            type="button"
            className={styles.profileAction}
            role="menuitem"
            onClick={() => void handleLogout()}
            disabled={logout.isPending}
          >
            {t('APP.LOGOUT')}
          </button>
        </div>
      ) : null}
    </div>
  );
}

export default ProfileMenu;
