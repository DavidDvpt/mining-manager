import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  getGetApiV1MeQueryKey,
  useGetApiV1Me,
  usePostApiV1Signin,
  usePostApiV1Logout,
} from '@/api/generated/miningManagerAPI';
import { AppRouter } from '@/router/AppRouter';
import ProfileMenu from '@/layouts/mainLayout/toolbar/ProfileMenu';
import { TopBarNav } from '@/layouts/mainLayout/toolbar/TopBarNav';

vi.mock('@/api/generated/miningManagerAPI', () => ({
  getGetApiV1MeQueryKey: vi.fn(() => ['/api/v1/me']),
  useGetApiV1Me: vi.fn(),
  usePostApiV1Signin: vi.fn(),
  usePostApiV1Logout: vi.fn(),
}));

const mockedGetApiV1MeQueryKey = vi.mocked(getGetApiV1MeQueryKey);
const mockedUseGetApiV1Me = vi.mocked(useGetApiV1Me);
const mockedUsePostApiV1Signin = vi.mocked(usePostApiV1Signin);
const mockedUsePostApiV1Logout = vi.mocked(usePostApiV1Logout);

/** Render the current pathname so navigation assertions do not depend on browser history. */
function LocationProbe() {
  return <output data-testid="location">{useLocation().pathname}</output>;
}

/** Create an isolated query client for a navigation test. */
function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
}

/** Render a component with the providers required by the authenticated UI. */
function renderWithProviders(ui: ReactNode, initialEntry = '/') {
  return render(
    <QueryClientProvider client={createTestQueryClient()}>
      <MemoryRouter initialEntries={[initialEntry]}>
        {ui}
        <LocationProbe />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('navigation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedGetApiV1MeQueryKey.mockReturnValue(['/api/v1/me']);
    mockedUseGetApiV1Me.mockReturnValue({
      data: undefined,
      isPending: false,
    } as ReturnType<typeof useGetApiV1Me>);
    mockedUsePostApiV1Signin.mockReturnValue({
      error: null,
      isPending: false,
    } as ReturnType<typeof usePostApiV1Signin>);
  });

  it('redirects unauthenticated users to signin from a protected route', async () => {
    renderWithProviders(<AppRouter />);

    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/signin');
    });
  });

  it('exposes the topbar navigation links', () => {
    renderWithProviders(<TopBarNav />);

    expect(screen.getByRole('link', { name: 'Transactions' }).getAttribute('href')).toBe(
      '/transactions',
    );
    expect(screen.getByRole('link', { name: 'Mining' }).getAttribute('href')).toBe(
      '/mining',
    );
    expect(screen.getByRole('link', { name: 'Storage' }).getAttribute('href')).toBe(
      '/storage',
    );
  });

  it('redirects to signin after a successful profile logout', async () => {
    const mutateAsync = vi.fn().mockResolvedValue(undefined);
    mockedUseGetApiV1Me.mockReturnValue({
      data: { pseudo: 'Test user' },
      isPending: false,
    } as ReturnType<typeof useGetApiV1Me>);
    mockedUsePostApiV1Logout.mockReturnValue({
      mutateAsync,
      isPending: false,
    } as unknown as ReturnType<typeof usePostApiV1Logout>);

    renderWithProviders(<ProfileMenu />);

    fireEvent.click(screen.getByRole('button', { name: 'Open profile menu' }));
    fireEvent.click(screen.getByRole('menuitem', { name: 'Log out' }));

    await waitFor(() => {
      expect(mutateAsync).toHaveBeenCalledOnce();
      expect(screen.getByTestId('location').textContent).toBe('/signin');
    });
  });

  it('stays on the current page when profile logout fails', async () => {
    const mutateAsync = vi.fn().mockRejectedValue(new Error('logout failed'));
    mockedUseGetApiV1Me.mockReturnValue({
      data: { pseudo: 'Test user' },
      isPending: false,
    } as ReturnType<typeof useGetApiV1Me>);
    mockedUsePostApiV1Logout.mockReturnValue({
      mutateAsync,
      isPending: false,
    } as unknown as ReturnType<typeof usePostApiV1Logout>);

    renderWithProviders(<ProfileMenu />);

    fireEvent.click(screen.getByRole('button', { name: 'Open profile menu' }));
    fireEvent.click(screen.getByRole('menuitem', { name: 'Log out' }));

    await waitFor(() => expect(mutateAsync).toHaveBeenCalledOnce());
    expect(screen.getByTestId('location').textContent).toBe('/');
  });
});
