import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { queryClient } from './lib/react-query/queryClient';
import { GuestOnly } from './modules/auth/guards/GuestOnly';
import { RequireAuth } from './modules/auth/guards/RequireAuth';
import SignInPage from './pages/signinPage/SignInPage';

/** Render providers and route public and authenticated application areas. */
export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<GuestOnly />}>
            <Route path="/signin" element={<SignInPage />} />
          </Route>
          <Route element={<RequireAuth />}>
            <Route path="/" element={<p>Mining Manager</p>} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
