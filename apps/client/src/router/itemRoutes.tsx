import ItemPageContent from '@/pages/itemPage/ItemPageContent';
import ItemPageLayout from '@/pages/itemPage/ItemPageLayout';
import RunningTransactions from '@/pages/itemPage/RunningTransactionsRoute';
import { ITEM_ROUTES, ITEM_SUB_ROUTES } from '@/router/constants';
import itemModalRoutes from '@/router/ItemModalRoutes';
import { Navigate, Route } from 'react-router-dom';
import { JSX } from 'react/jsx-runtime';

const { materials, ...others } = ITEM_ROUTES;

function ItemRoutes(props: string[]): JSX.Element {
  return (
    <Route path="items" element={<ItemPageLayout />}>
      <Route index element={<Navigate to="materials" replace />} />

      {Object.entries(others).map(([path, kind]): JSX.Element => (
        <Route key={path} path={path} element={<ItemPageContent kind={kind} />}>
          {itemModalRoutes()}
        </Route>
      ))}

      <Route path="materials" element={<ItemPageContent kind="material" />}>
        {itemModalRoutes()}
      </Route>

      {Object.entries(ITEM_SUB_ROUTES).map(([path, subKind]): JSX.Element => (
        <Route
          key={path}
          path={`materials/${path}`}
          element={<ItemPageContent kind="material" subKind={subKind} />}
        >
          {itemModalRoutes()}
        </Route>
      ))}

      {/* Transactions en cours */}
    </Route>
  );
}

export default ItemRoutes;
