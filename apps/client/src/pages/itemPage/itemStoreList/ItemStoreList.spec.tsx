import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ItemStoreList } from './ItemStoreList';
import type { ItemStoreRow } from '@/shared/types/listItem';

const createRow = (stock: number): ItemStoreRow => ({
  id: `material-${stock}`,
  name: 'Oil',
  kind: 'material',
  imageUrl: null,
  isRare: false,
  isUntradeable: false,
  tt: 1,
  decay: null,
  stock,
  details: {},
});

describe('ItemStoreList', () => {
  it('keeps the sell column space but hides its button when stock is empty', () => {
    render(<ItemStoreList kind="material" rows={[createRow(0)]} />);

    expect(screen.getByText('Stock')).toBeTruthy();
    expect(screen.getByText('0')).toBeTruthy();
    expect(
      document.querySelector('button[aria-label="Sell"]')?.getAttribute('aria-hidden'),
    ).toBe('true');
  });

  it('exposes the sell action when stock is available', () => {
    const onSell = vi.fn();
    render(<ItemStoreList kind="material" rows={[createRow(2)]} onSell={onSell} />);

    fireEvent.click(screen.getByRole('button', { name: 'Sell' }));

    expect(onSell).toHaveBeenCalledWith(expect.objectContaining({ stock: 2 }));
  });
});
