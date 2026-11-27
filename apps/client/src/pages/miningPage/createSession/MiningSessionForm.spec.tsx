import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
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
Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
  configurable: true,
  value: vi.fn(),
});

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
          details: { ammoBurn: 10, isLimited: true, depth: '250' },
        },
        {
          id: 'unlimited',
          name: 'Unlimited finder',
          imgId: null,
          economy: { decay: '0.00220' },
          details: { ammoBurn: 10, isLimited: false, depth: '350' },
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
        { id: 'f6', item: { id: 'finder' }, tt: '10', tier: 6 },
        { id: 'fu', item: { id: 'unlimited' }, tt: '1', tier: 2 },
        { id: 'fu2', item: { id: 'unlimited' }, tt: '2.12340', tier: 3 },
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

/** Open the accessible finder picker and choose a specific lot. */
function selectFinder(trigger: string, option: RegExp): void {
  fireEvent.keyDown(screen.getByRole('combobox', { name: trigger }), {
    key: 'ArrowDown',
  });
  fireEvent.click(
    within(screen.getByRole('listbox')).getByRole('option', { name: option }),
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
    fireEvent.keyDown(
      screen.getByRole('combobox', { name: 'Sélectionner un finder' }),
      { key: 'ArrowDown' },
    );
    const options = within(screen.getByRole('listbox'));
    const finderOption = options.getByRole('option', {
      name: /^Finder \(L\) · T4 10,00$/,
    });
    expect(
      within(finderOption).getByText('10,00').previousElementSibling?.tagName,
    ).toBe('BR');
    expect(
      options.getByRole('option', { name: /^Unlimited finder · T3 2,1234$/ }),
    ).toBeTruthy();
    fireEvent.click(finderOption);
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

  it('shows amplifier choices only while a finder is selected', async () => {
    renderCreation();
    const message =
      'Vous devez choisir un finder pour accéder au choix d’amplificateurs.';
    expect(screen.getByText(message)).toBeTruthy();
    expect(
      screen.queryByRole('radio', { name: 'Sans amplificateur' }),
    ).toBeNull();

    selectFinder('Sélectionner un finder', /Finder \(L\).*T4/);
    expect(screen.queryByText(message)).toBeNull();
    expect(screen.getByRole('radio', { name: /Amp 1/ })).toBeTruthy();

    await act(async () => {
      fireEvent.click(
        screen.getByRole('button', { name: 'Retirer Finder (L) · T4' }),
      );
    });
    expect(screen.getByText(message)).toBeTruthy();
    expect(screen.queryByRole('radio', { name: /Amp 1/ })).toBeNull();
  });

  it('replaces the amplifier session cost only when requested clicks exceed capacity', async () => {
    renderCreation();
    selectFinder('Sélectionner un finder', /Unlimited finder.*T2/);
    const clicks = screen.getByLabelText('Nombre de clics');
    fireEvent.click(screen.getByRole('radio', { name: /Amp 1/ }));
    const amplifier = within(
      screen.getByRole('radio', { name: /Amp 1/ }).closest('label')!,
    );
    await act(async () => {
      fireEvent.change(clicks, { target: { value: '91' } });
    });
    expect(amplifier.getByText('182.00 PED pour cette session')).toBeTruthy();

    await act(async () => {
      fireEvent.change(clicks, { target: { value: '92' } });
    });
    expect(amplifier.getByText('Quantité insuffisante')).toBeTruthy();
    expect(amplifier.queryByText(/PED pour cette session/)).toBeNull();

    await act(async () => {
      fireEvent.change(clicks, { target: { value: '91' } });
    });
    expect(amplifier.getByText('182.00 PED pour cette session')).toBeTruthy();
  });

  it('clears selected enhancers when adding a needed tier-zero finder', async () => {
    renderCreation();
    fireEvent.change(screen.getByLabelText('Nombre de clics'), {
      target: { value: '150' },
    });
    selectFinder('Sélectionner un finder', /Finder \(L\).*T4.*10,00/);
    fireEvent.change(screen.getByLabelText('Socket 1'), {
      target: { value: 'enhancer' },
    });
    fireEvent.click(
      screen.getByRole('button', { name: 'Ajouter un finder compatible' }),
    );
    fireEvent.click(
      within(screen.getByRole('listbox')).getByRole('option', {
        name: /Finder \(L\).*T0/,
      }),
    );
    expect(screen.queryByLabelText('Socket 1')).toBeNull();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Excavator · T0' }));
    fireEvent.click(screen.getByRole('button', { name: 'Créer la session' }));
    await waitFor(() =>
      expect(mocks.create.mock.calls[0][0].data.finderEnhancers).toEqual({}),
    );
  });

  it('adds only same-model lots when needed and displays the allocated costs per lot', async () => {
    renderCreation();
    expect(
      screen.getByRole('heading', { name: 'Setup de recherche' }),
    ).toBeTruthy();
    selectFinder('Sélectionner un finder', /Finder \(L\).*T4/);
    expect(screen.getByText('Finder (L) · T4')).toBeTruthy();
    expect(screen.getByText('Profondeur : 250,00 m')).toBeTruthy();
    expect(
      screen.queryByRole('combobox', { name: 'Sélectionner un finder' }),
    ).toBeNull();
    expect(
      screen.queryByRole('button', { name: 'Ajouter un finder compatible' }),
    ).toBeNull();
    fireEvent.change(screen.getByLabelText('Nombre de clics'), {
      target: { value: '150' },
    });
    const addFinder = screen.getByRole('button', {
      name: 'Ajouter un finder compatible',
    });
    expect(screen.queryByRole('listbox')).toBeNull();
    fireEvent.click(addFinder);
    const options = within(screen.getByRole('listbox'));
    expect(options.getAllByRole('option')).toHaveLength(2);
    expect(options.queryByRole('option', { name: /Unlimited/ })).toBeNull();
    fireEvent.click(options.getByRole('option', { name: /Finder \(L\).*T0/ }));
    expect(
      screen.queryByRole('combobox', { name: 'Ajouter un finder compatible' }),
    ).toBeNull();
    expect(screen.getByText('Decay · 10,00 PED')).toBeTruthy();
    expect(screen.getByText('Decay · 5,00 PED')).toBeTruthy();
    expect(screen.getByText('Munitions · 50,00 PED')).toBeTruthy();
    expect(screen.getByText('Munitions · 25,00 PED')).toBeTruthy();

    fireEvent.change(screen.getByLabelText('Nombre de clics'), {
      target: { value: '250' },
    });
    fireEvent.click(
      screen.getByRole('button', { name: 'Ajouter un finder compatible' }),
    );
    fireEvent.click(
      within(screen.getByRole('listbox')).getByRole('option', {
        name: /Finder \(L\).*T6/,
      }),
    );
    expect(
      screen.getAllByRole('button', { name: /Retirer Finder/ }),
    ).toHaveLength(3);
    expect(screen.getByText('Munitions · 25,00 PED')).toBeTruthy();

    await act(async () => {
      fireEvent.click(
        screen.getByRole('button', { name: 'Retirer Finder (L) · T6' }),
      );
    });
    expect(screen.queryByText('Finder (L) · T6')).toBeNull();
    expect(screen.getByText('Finder (L) · T4')).toBeTruthy();
    expect(screen.getByText('Finder (L) · T0')).toBeTruthy();
    selectFinder('Ajouter un finder compatible', /Finder \(L\).*T6/);

    fireEvent.change(screen.getByLabelText('Nombre de clics'), {
      target: { value: '100' },
    });
    await waitFor(() =>
      expect(
        screen.queryByRole('button', { name: 'Retirer Finder (L) · T0' }),
      ).toBeNull(),
    );
    expect(screen.getByText('Finder (L) · T4')).toBeTruthy();

    await act(async () => {
      fireEvent.click(
        screen.getByRole('button', { name: 'Retirer Finder (L) · T4' }),
      );
    });
    expect(screen.queryByText('Finder (L) · T4')).toBeNull();
    selectFinder('Sélectionner un finder', /Unlimited finder.*T2.*1,00/);
    fireEvent.change(screen.getByLabelText('Nombre de clics'), {
      target: { value: '1' },
    });
    expect(screen.getByText('Decay · 0,0022 PED')).toBeTruthy();
    fireEvent.change(screen.getByLabelText('Nombre de clics'), {
      target: { value: '200' },
    });
    expect(
      screen.queryByRole('button', { name: 'Ajouter un finder compatible' }),
    ).toBeNull();
    expect(screen.getByText('Decay · 0,44 PED')).toBeTruthy();
    expect(screen.getByText('Munitions · 100,00 PED')).toBeTruthy();
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
