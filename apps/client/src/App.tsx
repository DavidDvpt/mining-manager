import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

import { queryClient } from '@/lib/react-query/queryClient';
import { AppRouter } from '@/router/AppRouter';

/** Render application-wide providers and the browser router. */
export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
