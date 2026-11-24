import BuyTransactionRoute from '@/pages/itemPage/BuyTransactionRoute';
import SellTransactionRoute from '@/pages/itemPage/SellTransactionRoute';
import ToolEditRoute from '@/pages/itemPage/ToolEditRoute';
import { Route } from 'react-router-dom';
import { JSX } from 'react/jsx-runtime';

/** Declare resource action routes, including the intermediate equipment sale selection. */
function itemModalRoutes(): JSX.Element {
  return (
    <>
      <Route index element={null} />

      <Route path=":id">
        <Route path="buy" element={<BuyTransactionRoute />} />
        <Route path="sell">
          <Route index element={<SellTransactionRoute />} />
          <Route
            path="item-choice"
            element={<SellTransactionRoute isChoosing />}
          />
        </Route>
        <Route path="edit" element={<ToolEditRoute />} />
      </Route>
    </>
  );
}

export default itemModalRoutes;
