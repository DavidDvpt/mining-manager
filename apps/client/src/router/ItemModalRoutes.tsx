import BuyTransactionRoute from '@/pages/itemPage/BuyTransactionRoute';
import RunningTransactionsRoute from '@/pages/itemPage/RunningTransactionsRoute';
import SellTransactionRoute from '@/pages/itemPage/SellTransactionRoute';
import ToolEditRoute from '@/pages/itemPage/ToolEditRoute';
import { Route } from 'react-router-dom';

function itemModalRoutes(): import('react').JSX.Element {
  return (
    <>
      <Route index element={null} />
      <Route
        path="running-transactions"
        element={<RunningTransactionsRoute />}
      />
      <Route path="buy" element={<BuyTransactionRoute />} />
      <Route path="sell" element={<SellTransactionRoute />} />
      <Route path=":id/edit" element={<ToolEditRoute />} />
    </>
  );
}

export default itemModalRoutes;
