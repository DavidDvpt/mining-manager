import { Outlet } from 'react-router-dom';

import { useGetApiV1MaterialTypes } from '@/api/generated/miningManagerAPI';
import SidebarLayout from '@/layouts/sidebarLayout';
import { useTranslations } from '@/i18n/useTranslations';

import { transactionButtons } from './constants';

/** Render the item catalogue inside the shared sidebar workspace. */
function ItemPageLayout(): import('react').JSX.Element {
  const { t } = useTranslations();
  const { data: materialTypes = [] } = useGetApiV1MaterialTypes();

  return (
    <SidebarLayout
      buttons={transactionButtons(t, materialTypes)}
      defaultButtonId="finder"
      sidebarLabel={t('TRANSACTIONS.SIDEBAR_LABEL')}
    >
      <Outlet context={{ materialTypes }} />
    </SidebarLayout>
  );
}

export default ItemPageLayout;
