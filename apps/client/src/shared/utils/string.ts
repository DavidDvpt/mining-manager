export function toSlug(value: string) {
  if (!value) return '';

  return value.toLowerCase().replace(' ', '-');
}
