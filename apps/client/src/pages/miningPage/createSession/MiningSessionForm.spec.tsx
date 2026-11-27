import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import MiningSessionForm from './MiningSessionForm';

/** Supply browser resize observation for Radix controls in JSDOM. */
class TestResizeObserver {
  /** JSDOM has no layout to observe. */
  observe(): void {
    /* JSDOM does not calculate layout. */
  }
  /** Release a synthetic observation. */
  unobserve(): void {
    /* JSDOM does not calculate layout. */
  }
  /** Release all synthetic observations. */
  disconnect(): void {
    /* No synthetic observer to disconnect. */
  }
}
vi.stubGlobal('ResizeObserver', TestResizeObserver);

const mocks = vi.hoisted(() => ({
  create: vi.fn(),
  current: {
    data: null as null | { id: string },
    isPending: false,
    isError: false,
  },
}));
vi.mock('@/api/generated/miningManagerAPI', () => ({
  getGetApiV1MiningCurrentQueryKey: () => ['/api/v1/mining/current'],
  useGetApiV1MiningCurrent: () => mocks.current,
  usePostApiV1MiningCreate: () => ({
    mutateAsync: mocks.create,
    isPending: false,
    error: null,
  }),
  useGetApiV1Planet: () => ({ data: [{ id: 'planet', name: 'Calypso' }] }),
  useGetApiV1PlanetPlanetIdZone: () => ({ data: [] }),
  getGetApiV1PlanetPlanetIdZoneQueryKey: () => ['zones'],
}));
vi.mock('./useMiningEquipment', () => ({
  useMiningEquipment: () => ({
    isPending: false,
    isError: false,
    equipment: {
      finders: [
        {
          id: 'finder',
          name: 'Finder (L)',
          imgId: null,
          economy: { decay: '0.1' },
          details: { ammoBurn: 10, isLimited: true },
        },
      ],
      excavators: [
        {
          id: 'excavator',
          name: 'Excavator',
          imgId: null,
          economy: { decay: '1' },
          details: { isLimited: false },
        },
      ],
      amplifiers: [1, 2].map((id) => ({
        id: `amp${id}`,
        name: `Amp ${id}`,
        imgId: null,
        economy: { decay: '2' },
        details: { isLimited: true },
      })),
      enhancers: [
        {
          id: 'enhancer',
          name: 'Depth enhancer',
          imgId: null,
          economy: { tt: '0.8' },
          details: { tool: 'FINDER', socket: 1 },
        },
      ],
      enhancerStock: { enhancer: 5 },
      lots: [
        { id: 'f4', item: { id: 'finder' }, tt: '10', tier: 4 },
        { id: 'f0', item: { id: 'finder' }, tt: '10', tier: 0 },
        { id: 'e0', item: { id: 'excavator' }, tt: '0', tier: 0 },
        { id: 'a1', item: { id: 'amp1' }, tt: '183', tier: 0 },
        { id: 'a2', item: { id: 'amp2' }, tt: '183', tier: 0 },
      ],
    },
  }),
}));

/** Display the active URL to verify modal closure and post-create navigation. */
function LocationProbe() {
  return <output data-testid="location">{useLocation().pathname}</output>;
}

/** Mount the real modal/form with only network and stock sources replaced. */
function renderCreation() {
  return render(
    <QueryClientProvider
      client={
        new QueryClient({ defaultOptions: { queries: { retry: false } } })
      }
    >
      <MemoryRouter initialEntries={['/mining/create']}>
        <Routes>
          <Route path="/mining/create" element={<MiningSessionForm />} />
          <Route path="*" element={<p>Mining</p>} />
        </Routes>
        <LocationProbe />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('mining creation route', () => {
  const originalLanguage = document.documentElement.lang;
  afterEach(() => {
    document.documentElement.lang = originalLanguage;
  });
  beforeEach(() => {
    document.documentElement.lang = 'fr';
    mocks.current.data = null;
    mocks.create.mockReset().mockResolvedValue({ sessionId: 'created' });
  });

  it('opens a modal, selects one amp model and submits lot IDs through the existing contract', async () => {
    renderCreation();
    expect(screen.getByRole('dialog')).toBeTruthy();
    expect(screen.getByText(/Coût estimé/).textContent).toMatch(
      /PED TT.*PED TTC/,
    );
    fireEvent.change(screen.getByLabelText('Modèle de finder'), {
      target: { value: 'finder' },
    });
    fireEvent.click(screen.getByRole('checkbox', { name: 'Finder (L) · T4' }));
    fireEvent.click(screen.getByRole('checkbox', { name: 'Excavator · T0' }));
    fireEvent.click(screen.getByRole('radio', { name: /Amp 1/ }));
    fireEvent.click(screen.getByRole('radio', { name: /Amp 2/ }));
    expect(
      screen.getByRole('radio', { name: /Amp 1/ }).getAttribute('aria-checked'),
    ).toBe('false');
    fireEvent.click(screen.getByRole('button', { name: 'Créer la session' }));
    await waitFor(() =>
      expect(mocks.create).toHaveBeenCalledWith({
        data: {
          clics: 1,
          searchType: 'E',
          finder: ['f4'],
          excavators: ['e0'],
          sessionZone: null,
          finderAmplifiers: ['a2'],
          finderEnhancers: {},
          excavatorEnhancers: {},
        },
      }),
    );
    await waitFor(() =>
      expect(screen.getByTestId('location').textContent).toBe(
        '/mining/created/running',
      ),
    );
  });

  it('clears selected enhancers when adding a needed tier-zero finder', async () => {
    renderCreation();
    fireEvent.change(screen.getByLabelText('Nombre de clics'), {
      target: { value: '150' },
    });
    fireEvent.change(screen.getByLabelText('Modèle de finder'), {
      target: { value: 'finder' },
    });
    fireEvent.click(screen.getByRole('checkbox', { name: 'Finder (L) · T4' }));
    fireEvent.change(screen.getByLabelText('Socket 1'), {
      target: { value: 'enhancer' },
    });
    fireEvent.click(screen.getByRole('checkbox', { name: 'Finder (L) · T0' }));
    expect(screen.queryByLabelText('Socket 1')).toBeNull();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Excavator · T0' }));
    fireEvent.click(screen.getByRole('button', { name: 'Créer la session' }));
    await waitFor(() =>
      expect(mocks.create.mock.calls[0][0].data.finderEnhancers).toEqual({}),
    );
  });

  it('hides unnecessary finders and restores choices when the requested decay increases', async () => {
    renderCreation();
    fireEvent.change(screen.getByLabelText('Modèle de finder'), {
      target: { value: 'finder' },
    });
    fireEvent.click(screen.getByRole('checkbox', { name: 'Finder (L) · T4' }));
    expect(
      screen.queryByRole('checkbox', { name: 'Finder (L) · T0' }),
    ).toBeNull();
    fireEvent.change(screen.getByLabelText('Nombre de clics'), {
      target: { value: '150' },
    });
    fireEvent.click(screen.getByRole('checkbox', { name: 'Finder (L) · T0' }));
    expect(screen.getAllByRole('checkbox', { name: /Finder/ })).toHaveLength(2);
    fireEvent.change(screen.getByLabelText('Nombre de clics'), {
      target: { value: '100' },
    });
    await waitFor(() =>
      expect(screen.getAllByRole('checkbox', { name: /Finder/ })).toHaveLength(
        1,
      ),
    );
    fireEvent.click(screen.getByRole('checkbox', { name: /Finder/ }));
    expect(screen.getAllByRole('checkbox', { name: /Finder/ })).toHaveLength(2);
    await act(async () => {
      await Promise.resolve();
    });
  });

  it('cancels to mining and refuses direct creation when a session is already open', () => {
    const view = renderCreation();
    fireEvent.click(screen.getByRole('button', { name: 'Annuler' }));
    expect(screen.getByTestId('location').textContent).toBe('/mining');
    view.unmount();
    mocks.current.data = { id: 'open' };
    renderCreation();
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(screen.getByTestId('location').textContent).toBe(
      '/mining/open/running',
    );
  });
});
