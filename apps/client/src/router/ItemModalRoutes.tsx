import BuyTransactionRoute from '@/pages/itemPage/BuyTransactionRoute';
import SellTransactionRoute from '@/pages/itemPage/SellTransactionRoute';
import ToolEditRoute from '@/pages/itemPage/ToolEditRoute';
import { Route } from 'react-router-dom';

function itemModalRoutes() {
  return (
    <>
      <Route index element={null} />
      <Route path="buy" element={<BuyTransactionRoute />} />
      <Route path="sell" element={<SellTransactionRoute />} />
      <Route path=":id/edit" element={<ToolEditRoute />} />
    </>
  );
}

export default itemModalRoutes;
