import { Navigate, Route, Routes } from 'react-router-dom';

import MiningPage from '@/pages/miningPage/MiningPage';
import MiningPageContent from '@/pages/miningPage/MiningPageContent';
import MiningSessionForm from '@/pages/miningPage/createSession';
import HomePage from '@/pages/homePage/HomePage';
import MainLayout from '@/layouts/mainLayout/MainLayout';
import SignInPage from '@/pages/signinPage/SignInPage';
import { GuestOnly } from '@/router/guards/GuestOnly';
import { RequireAuth } from '@/router/guards/RequireAuth';
import itemRoutes from '@/router/itemRoutes';
import { useGetApiV1MaterialTypes } from '@/api/generated/miningManagerAPI';
import { toSlug } from '@/shared/utils/string';

/** Render the public and authenticated business routes. */
export function AppRouter(): import('react').JSX.Element {
  const { data: materialTypes = [] } = useGetApiV1MaterialTypes();
  const parsed = materialTypes?.map(({ name }): string => toSlug(name)) ?? [];
  return (
    <Routes>
      <Route element={<GuestOnly />}>
        <Route path="/signin" element={<SignInPage />} />
      </Route>
      <Route element={<RequireAuth />}>
        <Route element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />

          {itemRoutes(parsed)}

          <Route path="/mining" element={<MiningPage />}>
            <Route element={<MiningPageContent />}>
              <Route index element={null} />
              <Route path="create" element={<MiningSessionForm />} />
              <Route path="current" element={null} />
              <Route path=":sessionId/running" element={null} />
              <Route path=":sessionId/close" element={null} />
            </Route>
          </Route>
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default AppRouter;
