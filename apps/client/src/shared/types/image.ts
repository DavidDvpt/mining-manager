/** Supported display sizes for an Entropia item image. */
export type EntropiaImageSize = 'small' | 'medium' | 'large';

/** Props accepted by the shared Entropia item image component. */
export type EntropiaImageProps = {
  /** URL returned by the entropia-images service; null renders the fallback. */
  url: string | null;
  /** Alternative text used by screen readers and the fallback label. */
  alt: string;
  /** Display size: 40px, 80px, or 160px square. */
  size?: EntropiaImageSize;
  /** Optional class names applied to the image container. */
  className?: string;
};
