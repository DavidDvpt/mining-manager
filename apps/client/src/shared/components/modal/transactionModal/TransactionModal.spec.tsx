import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { ReactNode } from 'react';
import { TransactionModal } from './TransactionModal';
import type { ItemStoreRow } from '@/shared/types/listItem';

vi.stubGlobal(
  'ResizeObserver',
  class ResizeObserver {
    observe() {
      return undefined;
    }
    unobserve() {
      return undefined;
    }
    disconnect() {
      return undefined;
    }
  },
);

const mutationMocks = vi.hoisted(() => ({
  buyStackable: vi.fn(),
  buyUnstackable: vi.fn(),
  sellStackable: vi.fn(),
  sellUnstackable: vi.fn(),
}));

const stockQueryKey = ['/api/v1/storage/material/stock'] as const;

vi.mock('@/api/generated/miningManagerAPI', () => ({
  getGetApiV1ExcavatorsStockQueryKey: () => ['/api/v1/excavators/stock'],
  getGetApiV1FinderAmplifiersStockQueryKey: () => [
    '/api/v1/finder-amplifiers/stock',
  ],
  getGetApiV1FindersStockQueryKey: () => ['/api/v1/finders/stock'],
  getGetApiV1RefinersStockQueryKey: () => ['/api/v1/refiners/stock'],
  getGetApiV1StorageMaterialStockQueryKey: () => [
    '/api/v1/storage/material/stock',
  ],
  usePostApiV1TransactionBuyStackable: () => ({ mutateAsync: mutationMocks.buyStackable }),
  usePostApiV1TransactionBuyUnstackable: () => ({ mutateAsync: mutationMocks.buyUnstackable }),
  usePostApiV1TransactionSellStackable: () => ({ mutateAsync: mutationMocks.sellStackable }),
  usePostApiV1TransactionSellUnstackable: () => ({ mutateAsync: mutationMocks.sellUnstackable }),
}));

const renderTransactionModal = (
  children: ReactNode,
  queryClient = new QueryClient(),
) =>
  render(
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>,
  );

const stackableItem: ItemStoreRow = {
  id: 'material-1',
  name: 'Oil',
  kind: 'material',
  imageUrl: null,
  isRare: false,
  isUntradeable: false,
  tt: 10,
  decay: null,
  stock: 4,
  details: {},
};

const unstackableItem: ItemStoreRow = {
  ...stackableItem,
  id: 'finder-1',
  name: 'Finder',
  kind: 'finder',
};

describe('TransactionModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mutationMocks.buyStackable.mockResolvedValue(undefined);
    mutationMocks.buyUnstackable.mockResolvedValue(undefined);
    mutationMocks.sellStackable.mockResolvedValue(undefined);
    mutationMocks.sellUnstackable.mockResolvedValue(undefined);
  });

  it('focuses quantity for stackable transactions', async () => {
    renderTransactionModal(
      <TransactionModal
        item={stackableItem}
        lot={null}
        action="buy"
        open
        onOpenChange={vi.fn()}
      />,
    );

    await waitFor(() =>
      expect(document.activeElement).toBe(screen.getByLabelText('Quantity')),
    );
  });

  it('focuses TT for unstackable transactions', async () => {
    renderTransactionModal(
      <TransactionModal
        item={unstackableItem}
        lot={null}
        action="buy"
        open
        onOpenChange={vi.fn()}
      />,
    );

    await waitFor(() =>
      expect(document.activeElement).toBe(screen.getByLabelText('TT')),
    );
  });

  it('creates a stackable buy transaction and closes after success', async () => {
    const onOpenChange = vi.fn();

    renderTransactionModal(
      <TransactionModal
        item={stackableItem}
        lot={null}
        action="buy"
        open
        onOpenChange={onOpenChange}
      />,
    );

    const autoComputeCheckbox = screen.getByRole('checkbox', {
      name: 'Automatic calculation',
    });
    expect(autoComputeCheckbox.getAttribute('aria-checked')).toBe('false');

    fireEvent.click(screen.getByRole('button', { name: 'Valider' }));

    await waitFor(() => expect(mutationMocks.buyStackable).toHaveBeenCalledOnce());
    expect(mutationMocks.buyStackable.mock.calls[0][0].data).toMatchObject({
      item_id: 'material-1',
      kind: 'material',
      quantity: 1,
    });
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('creates an unstackable buy transaction', async () => {
    renderTransactionModal(
      <TransactionModal
        item={unstackableItem}
        lot={null}
        action="buy"
        open
        onOpenChange={vi.fn()}
      />,
    );

    fireEvent.change(screen.getByLabelText('TT'), {
      target: { value: '9.5' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Valider' }));

    await waitFor(() => expect(mutationMocks.buyUnstackable).toHaveBeenCalledOnce());
    expect(mutationMocks.buyUnstackable.mock.calls[0][0].data).toMatchObject({
      item_id: 'finder-1',
      kind: 'tool',
      quantity: 1,
      tt: 9.5,
    });
  });

  it('updates the material stock cache after a successful stackable buy', async () => {
    const queryClient = new QueryClient();
    queryClient.setQueryData<Record<string, number>>(stockQueryKey, {
      'material-1': 4,
    });

    renderTransactionModal(
      <TransactionModal
        item={stackableItem}
        lot={null}
        action="buy"
        open
        onOpenChange={vi.fn()}
      />,
      queryClient,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Valider' }));

    await waitFor(() => expect(mutationMocks.buyStackable).toHaveBeenCalledOnce());
    expect(queryClient.getQueryData(stockQueryKey)).toEqual({
      'material-1': 5,
    });
  });

  it('allows replacing a buy field through an empty intermediate value', async () => {
    renderTransactionModal(
      <TransactionModal
        item={stackableItem}
        lot={null}
        action="buy"
        open
        onOpenChange={vi.fn()}
      />,
    );

    const feeInput = screen.getByLabelText('Fee');
    fireEvent.change(feeInput, { target: { value: '' } });
    fireEvent.change(feeInput, { target: { value: '3' } });
    fireEvent.click(screen.getByRole('button', { name: 'Valider' }));

    await waitFor(() => expect(mutationMocks.buyStackable).toHaveBeenCalledOnce());
    expect(mutationMocks.buyStackable.mock.calls[0][0].data).toMatchObject({
      fee: 3,
    });
  });

  it('creates a stackable sell transaction', async () => {
    renderTransactionModal(
      <TransactionModal
        item={stackableItem}
        lot={null}
        action="sell"
        open
        onOpenChange={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Valider' }));

    await waitFor(() => expect(mutationMocks.sellStackable).toHaveBeenCalledOnce());
    expect(mutationMocks.sellStackable.mock.calls[0][0].data).toMatchObject({
      item_id: 'material-1',
      quantity: 1,
    });
  });

  it('rejects a stackable sale above available stock before mutation', async () => {
    const onOpenChange = vi.fn();

    renderTransactionModal(
      <TransactionModal
        item={stackableItem}
        lot={null}
        action="sell"
        open
        onOpenChange={onOpenChange}
      />,
    );

    fireEvent.change(screen.getByLabelText('Quantity'), {
      target: { value: '5' },
    });
    await waitFor(() =>
      expect((screen.getByLabelText('Quantity') as HTMLInputElement).value).toBe('5'),
    );
    fireEvent.click(screen.getByRole('button', { name: 'Valider' }));

    expect((await screen.findByRole('alert')).textContent).toContain(
      'quantity cannot exceed available stock',
    );
    expect(mutationMocks.sellStackable).not.toHaveBeenCalled();
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
  });

  it('creates an unstackable sell transaction from its lot', async () => {
    renderTransactionModal(
      <TransactionModal
        item={unstackableItem}
        lot={{
          id: 'lot-1',
          item: { id: 'finder-1', name: 'Finder' },
          tt: 10,
          tt_remaining: '10',
        } as never}
        action="sell"
        open
        onOpenChange={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Valider' }));

    await waitFor(() => expect(mutationMocks.sellUnstackable).toHaveBeenCalledOnce());
    expect(mutationMocks.sellUnstackable.mock.calls[0][0].data).toMatchObject({
      lot_id: 'lot-1',
      quantity: 1,
    });
  });

  it('rejects an unstackable sale above the item base TT before mutation', async () => {
    const onOpenChange = vi.fn();

    renderTransactionModal(
      <TransactionModal
        item={unstackableItem}
        lot={null}
        action="sell"
        open
        onOpenChange={onOpenChange}
      />,
    );

    fireEvent.change(screen.getByLabelText('TT'), {
      target: { value: '11' },
    });
    await waitFor(() =>
      expect((screen.getByLabelText('TT') as HTMLInputElement).value).toBe('11'),
    );
    fireEvent.click(screen.getByRole('button', { name: 'Valider' }));

    expect((await screen.findByRole('alert')).textContent).toContain(
      'TT cannot exceed the item base TT value',
    );
    expect(mutationMocks.sellUnstackable).not.toHaveBeenCalled();
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
  });
});
