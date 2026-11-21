export function toSlug(value: string): string {
  if (!value) return '';

  return value.toLowerCase().replace(' ', '-');
}
