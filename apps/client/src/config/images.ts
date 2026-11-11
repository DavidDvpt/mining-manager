import { env } from './env';

/** Build the image-depot URL for an item image identifier and requested size. */
export function getItemImageUrl(
  imageId: number | null,
  size: 'micro' | 'normal' = 'normal',
): string | null {
  if (imageId === null) {
    return null;
  }

  const baseUrl = env.VITE_IMAGE_BASE_URL.replace(/\/+$/, '');
  return `${baseUrl}/${encodeURIComponent(String(imageId))}?size=${size}`;
}
