import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { TransactionModal } from './TransactionModal';
import type { ItemRow } from '@/shared/types';
import { TransactionPricing } from './transactionPricing';

/** Supply the browser resize API required by the shared Radix checkbox in jsdom. */
class TestResizeObserver {
  /** Accept observation requests without performing browser layout in jsdom. */
  observe(): void {
    /* jsdom has no layout. */
  }
  /** Stop observing an individual checkbox without retaining layout resources. */
  unobserve(): void {
    /* jsdom has no layout. */
  }
  /** Release the no-op observation when the checkbox unmounts. */
  disconnect(): void {
    /* No resources are retained. */
  }
}
vi.stubGlobal('ResizeObserver', TestResizeObserver);

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
  details: { isStackable: true, type: { id: 'ore', name: 'Ore' } },
};
const tool: ItemRow = {
  ...item,
  id: 'finder-1',
  name: 'Finder',
  kind: 'finder',
  details: {
    isStackable: false,
    isLimited: false,
    usePerMinute: null,
    depth: null,
    range: null,
    ammoBurn: null,
  },
};

/** Resolve the actual form for native submission tests, failing clearly if its shell is missing. */
function transactionForm(): HTMLFormElement {
  const form = screen.getByRole('button', { name: 'Confirm' }).closest('form');
  if (!form) throw new Error('Missing transaction form');
  return form;
}

afterEach(cleanup);

describe('TransactionModal', () => {
  it('calculates a stackable buy using Pricing and submits its validated fields', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <TransactionModal
        item={item}
        action="buy"
        onClose={vi.fn()}
        onSubmit={onSubmit}
      />,
    );
    fireEvent.change(screen.getByLabelText('Quantity'), {
      target: { value: '3' },
    });
    await waitFor(() =>
      expect((screen.getByLabelText('TT') as HTMLInputElement).value).toBe(
        '30',
      ),
    );
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          quantity: 3,
          tt: 30,
          ttc: 30,
          type_detail: 'AUCTION',
        }),
      ),
    );
  });

  it('keeps identical purchase count separate from per-instance pricing and shows totals', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <TransactionModal
        item={tool}
        action="buy"
        onClose={vi.fn()}
        onSubmit={onSubmit}
      />,
    );
    fireEvent.change(screen.getByLabelText('Purchase quantity'), {
      target: { value: '3' },
    });
    await waitFor(() => expect(screen.getAllByText('30 PED')).toHaveLength(2));
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          quantity: 1,
          purchase_quantity: 3,
          tt: 10,
          ttc: 10,
        }),
      ),
    );
  });

  it('validates available sale stock and nonnegative prices', async () => {
    const onSubmit = vi.fn();
    render(
      <TransactionModal
        item={item}
        stock={2}
        action="sell"
        onClose={vi.fn()}
        onSubmit={onSubmit}
      />,
    );
    fireEvent.change(screen.getByLabelText('Quantity'), {
      target: { value: '3' },
    });
    fireEvent.submit(transactionForm());
    await screen.findByText('The quantity cannot exceed available stock.');
    expect(onSubmit).not.toHaveBeenCalled();
    fireEvent.change(screen.getByLabelText('TTC'), { target: { value: '' } });
    fireEvent.submit(transactionForm());
    await waitFor(() =>
      expect(screen.getByLabelText('TTC').getAttribute('aria-invalid')).toBe(
        'true',
      ),
    );
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('requires a positive integer purchase count for identical equipment', async () => {
    const onSubmit = vi.fn();
    render(
      <TransactionModal
        item={tool}
        action="buy"
        onClose={vi.fn()}
        onSubmit={onSubmit}
      />,
    );
    fireEvent.change(screen.getByLabelText('Purchase quantity'), {
      target: { value: '1.5' },
    });
    fireEvent.submit(transactionForm());
    await waitFor(() =>
      expect(
        screen.getByLabelText('Purchase quantity').getAttribute('aria-invalid'),
      ).toBe('true'),
    );
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('stores Auto Compute in the form and delegates toggle calculations to Pricing', async () => {
    const update = vi.spyOn(TransactionPricing.prototype, 'update');
    render(
      <TransactionModal
        item={tool}
        action="sell"
        onClose={vi.fn()}
        onSubmit={vi.fn()}
      />,
    );
    const checkbox = screen.getByRole('checkbox');
    expect(screen.getByLabelText('Fee').hasAttribute('readonly')).toBe(true);
    fireEvent.click(checkbox);
    expect(screen.getByLabelText('Fee').hasAttribute('readonly')).toBe(false);
    fireEvent.change(screen.getByLabelText('Fee'), { target: { value: '3' } });
    await waitFor(() => expect(update).toHaveBeenCalledWith('fee', 3, false));
    fireEvent.click(checkbox);
    await waitFor(() => expect(update).toHaveBeenCalledWith('fee', 3, true));
    expect(screen.getByLabelText('Fee').hasAttribute('readonly')).toBe(true);
    update.mockRestore();
  });

  it('prevents duplicate submission while pending and displays a failure for retry', async () => {
    let rejectSubmission: (error: Error) => void = (): void => undefined;
    const onSubmit = vi.fn(
      () =>
        new Promise<void>((_, reject): void => {
          rejectSubmission = reject;
        }),
    );
    render(
      <TransactionModal
        item={item}
        action="buy"
        onClose={vi.fn()}
        onSubmit={onSubmit}
      />,
    );
    const button = screen.getByRole('button', { name: 'Confirm' });
    fireEvent.click(button);
    await waitFor(() =>
      expect((button as HTMLButtonElement).disabled).toBe(true),
    );
    await act(async () => fireEvent.submit(transactionForm()));
    expect(onSubmit).toHaveBeenCalledOnce();
    rejectSubmission(new Error('Sale failed'));
    await screen.findByRole('alert');
    expect(screen.getByText('Sale failed')).toBeTruthy();
    await waitFor(() =>
      expect((button as HTMLButtonElement).disabled).toBe(false),
    );
  });
});
