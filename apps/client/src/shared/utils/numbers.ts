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
