import { TransactionBuyModal } from '@/shared';
import type { ItemRow } from '@/shared';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { JSX } from 'react/jsx-runtime';

/** Render the buy modal from the item serialized by the catalogue route. */
function BuyTransactionRoute(): JSX.Element | null {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const item = searchParams.get('item');

  if (!item) return null;

  const parsedItem: ItemRow = JSON.parse(item);

  return (
    <TransactionBuyModal
      item={parsedItem}
      onClose={() => {
        navigate('../..');
      }}
    />
  );
}

export default BuyTransactionRoute;
