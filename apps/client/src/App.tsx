import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'sonner';

import { queryClient } from '@/lib/react-query/queryClient';
import { AppRouter } from '@/router/AppRouter';

/** Render application providers, global toasts, and the browser router. */
export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster
        className="toast-container"
        position="bottom-right"
        duration={4000}
        toastOptions={{
          classNames: {
            toast: 'app-toast',
            success: 'app-toast-success',
            error: 'app-toast-error',
            info: 'app-toast-info',
          },
        }}
      />
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
