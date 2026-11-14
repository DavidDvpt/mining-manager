export type EditableNumber = number | undefined;

/** Format a decimal with a comma, preserving significant digits and at least two decimals. */
export function formatDecimalValue(value: unknown): string {
  if (value === null || value === undefined || value === '') {
    return '—';
  }

  const [integerPart, rawFraction = ''] = String(value)
    .replace(',', '.')
    .split('.');
  const fraction = rawFraction.replace(/0+$/, '');
  const paddedFraction = fraction.padEnd(2, '0');

  return `${integerPart},${paddedFraction}`;
}

/** Format a finite percentage value with a configurable number of decimal places. */
export function formatPercentageValue(value: number, decimalPlaces = 2): string {
  const safeDecimalPlaces = Math.min(100, Math.max(0, Math.trunc(decimalPlaces)));
  return (Number.isFinite(value) ? value : 0).toFixed(safeDecimalPlaces);
}

/** Convert an API numeric value into a finite number while preserving null. */
export function parseNumber(
  value: string | number | null | undefined,
): number | null {
  if (value === null || value === undefined || value === '') return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

/** Convert a possibly-null numeric value into a finite number with a zero fallback. */
export function numericValue(value: string | number | null | undefined): number {
  return parseNumber(value) ?? 0;
}

/** Preserve an empty numeric input while the user replaces it. */
export function parseInputValue(value: string): EditableNumber {
  if (value.trim() === '') return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? Math.max(0, parsed) : undefined;
}
