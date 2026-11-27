import { useNavigate } from 'react-router-dom';
import { ToolEditModal } from '@/shared/components/modal/toolEdit';
import { TransactionRouteStatus } from './TransactionRouteStatus';
import { useTransactionItem } from './useTransactionItem';

/** Load the URL item and close its edit modal back to the catalogue. */
function ToolEditRoute(): import('react').JSX.Element {
  const navigate = useNavigate();
  const { item, isLoading, isError } = useTransactionItem();

  /** Return to the current item category when editing finishes or is cancelled. */
  const close = (): void => navigate('../..');

  if (isLoading || isError || !item)
    return <TransactionRouteStatus loading={isLoading} onClose={close} />;

  return (
    <ToolEditModal
      item={item}
      open
      onOpenChange={(open): void => {
        if (!open) close();
      }}
    />
  );
}

export default ToolEditRoute;
