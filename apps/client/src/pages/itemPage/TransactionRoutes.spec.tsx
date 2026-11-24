import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  MemoryRouter,
  Outlet,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { AxiosRequestConfig } from 'axios';
import type {
  ItemSummaryResponse,
  UnstackableLotResponse,
} from '@/api/generated/model';
import itemModalRoutes from '@/router/ItemModalRoutes';

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

const request = vi.hoisted(() => vi.fn());
vi.mock('@/api/mutator/customInstance', () => ({ customInstance: request }));

const summary: ItemSummaryResponse = {
  id: 'item-1',
  name: 'Finder',
  imgId: 1,
  nexusId: null,
  weight: null,
  isUntradeable: false,
  isRare: false,
  isActive: true,
  nexusUrl: null,
  description: null,
  createdAt: null,
  updatedAt: null,
};
const equipment = {
  ...summary,
  economy: { tt: '10', decay: null, avgMuPercent: null, avgMuPlus: null },
  details: {
    isStackable: false,
    isLimited: false,
    usePerMinute: null,
    depth: null,
    range: null,
    ammoBurn: null,
  },
};
const material = {
  ...equipment,
  name: 'Oil',
  details: { isStackable: true, type: { id: 'ore', name: 'Ore' } },
};
const firstLot: UnstackableLotResponse = {
  id: 'lot-1',
  userId: 'user-1',
  type: 'TOOL',
  item: summary,
  qty: 1,
  reserved: 0,
  tier: 2,
  tt: '6.25',
  isDefault: false,
  createdAt: '2026-01-01',
  updatedAt: null,
  isActive: true,
};
let lots: UnstackableLotResponse[];
let stock: number;

/** Expose the current URL and the same item-kind outlet context as the catalogue page. */
function Catalogue({
  stackable,
}: {
  stackable: boolean;
}): import('react').JSX.Element {
  const location = useLocation();
  return (
    <>
      <output data-testid="url">
        {location.pathname}
        {location.search}
      </output>
      <Outlet context={{ kind: stackable ? 'material' : 'finder' }} />
    </>
  );
}

/** Exercise the production modal route hierarchy with real query hooks and an isolated transport. */
function renderWorkflow(path: string, stackable = false): QueryClient {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="items/materials/ore" element={<Catalogue stackable />}>
            {itemModalRoutes()}
          </Route>
          <Route
            path="items/finders"
            element={<Catalogue stackable={stackable} />}
          >
            {itemModalRoutes()}
          </Route>
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
  return client;
}

beforeEach(() => {
  stock = 4;
  lots = [firstLot, { ...firstLot, id: 'lot-2', tier: 3, tt: '8.50' }];
  request.mockReset();
  request.mockImplementation(
    async ({ url, method }: AxiosRequestConfig): Promise<unknown> => {
      if (method === 'POST') return { session_id: 'session-1' };
      if (url === '/api/v1/finders/item-1') return equipment;
      if (url === '/api/v1/materials/item-1') return material;
      if (url === '/api/v1/lots/unstackable/item/item-1') return lots;
      if (url === '/api/v1/lots/item-1')
        return { item: summary, lots: [], totalQuantity: stock };
      throw new Error(`Unexpected request: ${url}`);
    },
  );
});
afterEach(cleanup);

describe('transaction routes', () => {
  it('loads a stackable buy from the item ID on direct navigation without stock', async () => {
    renderWorkflow('/items/materials/ore/item-1/buy', true);
    await screen.findByLabelText('Quantity');
    fireEvent.change(screen.getByLabelText('Quantity'), {
      target: { value: '2' },
    });
    await waitFor(() =>
      expect((screen.getByLabelText('TT') as HTMLInputElement).value).toBe(
        '20',
      ),
    );
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() =>
      expect(request).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/api/v1/transaction/buy/stackable',
          data: expect.objectContaining({ item_id: 'item-1', quantity: 2 }),
        }),
        undefined,
      ),
    );
    await waitFor(() =>
      expect(screen.getByTestId('url').textContent).toBe(
        '/items/materials/ore',
      ),
    );
    expect(
      request.mock.calls.some(([config]) => config.url.includes('/lots/')),
    ).toBe(false);
  });

  it('loads stackable stock, submits the existing sale payload, and closes to the filtered catalogue', async () => {
    renderWorkflow('/items/materials/ore/item-1/sell', true);
    await screen.findByLabelText('Quantity');
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() =>
      expect(request).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/api/v1/transaction/sell/stackable',
          data: { item_id: 'item-1', quantity: 1, tt: 10, ttc: 10 },
        }),
        undefined,
      ),
    );
    await waitFor(() =>
      expect(screen.getByTestId('url').textContent).toBe(
        '/items/materials/ore',
      ),
    );
  });

  it('submits identical equipment purchases using purchase_quantity and per-instance prices', async () => {
    renderWorkflow('/items/finders/item-1/buy');
    fireEvent.change(await screen.findByLabelText('Purchase quantity'), {
      target: { value: '3' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() =>
      expect(request).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/api/v1/transaction/buy/unstackable',
          data: expect.objectContaining({
            quantity: 1,
            purchase_quantity: 3,
            tt: 10,
            ttc: 10,
            kind: 'tool',
          }),
        }),
        undefined,
      ),
    );
  });

  it('requires an explicit equipment choice, persists only its ID, and sells that exact lot', async () => {
    renderWorkflow('/items/finders/item-1/sell');
    const radios = await screen.findAllByRole('radio');
    expect(screen.getByTestId('url').textContent).toBe(
      '/items/finders/item-1/sell/item-choice',
    );
    expect(
      (screen.getByRole('button', { name: 'Confirm' }) as HTMLButtonElement)
        .disabled,
    ).toBe(true);
    fireEvent.click(radios[0]);
    fireEvent.click(radios[1]);
    expect((radios[0] as HTMLInputElement).checked).toBe(false);
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await screen.findByLabelText('TTC');
    expect(screen.getByTestId('url').textContent).toBe(
      '/items/finders/item-1/sell?lotId=lot-2',
    );
    expect((screen.getByLabelText('TT') as HTMLInputElement).value).toBe('8.5');
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() =>
      expect(request).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/api/v1/transaction/sell/unstackable',
          data: { quantity: 1, lot_id: 'lot-2', tt: 8.5, ttc: 9 },
        }),
        undefined,
      ),
    );
  });

  it('cancels lot selection back to the item category', async () => {
    renderWorkflow('/items/finders/item-1/sell/item-choice');
    await screen.findAllByRole('radio');
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    await waitFor(() =>
      expect(screen.getByTestId('url').textContent).toBe('/items/finders'),
    );
    expect(screen.queryByRole('dialog')).toBeNull();
  });

  it('resolves a selected lot after refresh without router state or serialized resources', async () => {
    renderWorkflow('/items/finders/item-1/sell?lotId=lot-1');
    await screen.findByLabelText('TTC');
    expect((screen.getByLabelText('TT') as HTMLInputElement).value).toBe(
      '6.25',
    );
    expect(screen.queryByRole('radio')).toBeNull();
  });

  it.each(['missing', 'reserved', 'inactive', 'foreign'])(
    'blocks a %s lot selected by URL',
    async (state) => {
      if (state === 'reserved') lots = [{ ...firstLot, reserved: 1 }];
      if (state === 'inactive') lots = [{ ...firstLot, isActive: false }];
      if (state === 'foreign')
        lots = [{ ...firstLot, item: { ...summary, id: 'other-item' } }];
      renderWorkflow(
        `/items/finders/item-1/sell?lotId=${state === 'missing' ? 'unknown' : 'lot-1'}`,
      );
      await screen.findByRole('alert');
      expect(screen.queryByLabelText('TTC')).toBeNull();
    },
  );

  it('rechecks lot availability before mutation when another operation reserves it', async () => {
    renderWorkflow('/items/finders/item-1/sell?lotId=lot-1');
    await screen.findByLabelText('TTC');
    lots = [{ ...firstLot, reserved: 1 }];
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await screen.findByRole('alert');
    expect(
      request.mock.calls.some(([config]) => config.method === 'POST'),
    ).toBe(false);
  });

  it('rechecks stock before mutation when it changes after opening', async () => {
    renderWorkflow('/items/materials/ore/item-1/sell', true);
    await screen.findByLabelText('TTC');
    stock = 0;
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await screen.findByText('The quantity cannot exceed available stock.');
    expect(
      request.mock.calls.some(([config]) => config.method === 'POST'),
    ).toBe(false);
  });

  it('shows loading and recoverable API errors instead of an empty workflow', async () => {
    let rejectRequest: (error: Error) => void = (): void => undefined;
    request.mockImplementation(
      () =>
        new Promise((_, reject): void => {
          rejectRequest = reject;
        }),
    );
    renderWorkflow('/items/finders/item-1/buy');
    expect(screen.getByRole('status')).toBeTruthy();
    await act(async () => rejectRequest(new Error('Missing item')));
    await screen.findByRole('alert');
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(screen.getByTestId('url').textContent).toBe('/items/finders');
  });
});
