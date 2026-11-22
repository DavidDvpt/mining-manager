import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, expect, it, vi } from 'vitest';
import type { ReactNode } from 'react';
import { TransactionModal } from './TransactionModal';
import type { ItemRow } from '@/shared/types';

const item: ItemRow = {
  id: 'material-1',
  name: 'Oil',
  kind: 'material',
  imageUrl: null,
  isRare: false,
  isUntradeable: false,
  tt: 10,
  decay: null,
  stock: 4,
  details: { isStackable: true },
};

const renderModal = (children: ReactNode) =>
  render(
    <QueryClientProvider client={new QueryClient()}>
      {children}
    </QueryClientProvider>,
  );

describe('TransactionModal', () => {
  it('renders the common shell and delegates submission to its caller', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);

    renderModal(
      <TransactionModal
        item={item}
        action="buy"
        onClose={vi.fn()}
        onSubmit={onSubmit}
      >
        <p>Buy fields</p>
      </TransactionModal>,
    );

    expect(screen.getByText('Buy fields')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Valider' }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledOnce());
  });
});
