import { render } from '@testing-library/react';

import App from './App';

describe('App', () => {
  it('renders the empty application shell', () => {
    const { baseElement } = render(<App />);
    expect(baseElement).toBeTruthy();
  });
});
