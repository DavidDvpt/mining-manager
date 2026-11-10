import { QueryClientProvider } from '@tanstack/react-query';

import { BrowserRouter } from 'react-router-dom';
import { queryClient } from './lib/react-query/queryClient';

/** Render the application providers and empty routing shell for the new UI. */
export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter />
    </QueryClientProvider>
  );
}

export default App;
