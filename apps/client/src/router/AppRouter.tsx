import { Navigate, Route, Routes } from 'react-router-dom';

import HomePage from '@/pages/homePage/HomePage';
import SignInPage from '@/pages/signinPage/SignInPage';
import TransactionPage from '@/pages/transactionPage/TransactionPage';
import { GuestOnly } from '@/router/guards/GuestOnly';
import { RequireAuth } from '@/router/guards/RequireAuth';

/** Render the public and authenticated business routes. */
export function AppRouter() {
  return (
    <Routes>
      <Route element={<GuestOnly />}>
        <Route path="/signin" element={<SignInPage />} />
      </Route>
      <Route element={<RequireAuth />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/transactions" element={<TransactionPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default AppRouter;
