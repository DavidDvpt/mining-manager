import { Modal } from '@/shared/components/modal';
import { Button } from '@/components/ui/button/button';
import { useTranslations } from '@/i18n/useTranslations';

/** Keep loading, missing-resource, and API error states visible and dismissible. */
export function TransactionRouteStatus({
  loading = false,
  onClose,
}: {
  loading?: boolean;
  onClose: () => void;
}): import('react').JSX.Element {
  const { t } = useTranslations();
  return (
    <Modal
      open
      onOpenChange={(open): void => {
        if (!open) onClose();
      }}
      title={t('TRANSACTIONS.TITLE')}
    >
      <p role={loading ? 'status' : 'alert'}>
        {t(loading ? 'ITEM_STORE.LOADING' : 'TRANSACTION_MODAL.UNAVAILABLE')}
      </p>
      <Button onClick={onClose}>{t('TOOL_EDIT_MODAL.CANCEL')}</Button>
    </Modal>
  );
}
