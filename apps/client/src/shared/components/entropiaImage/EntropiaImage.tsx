import { useState } from 'react';

import { cn } from '@/lib/utils/styles';
import type { EntropiaImageProps } from '@/shared/types/image';
import styles from './entropia-image.module.scss';

/** Display an Entropia item image with fixed shared sizes and an error fallback. */
export function EntropiaImage({
  url,
  alt,
  size = 'medium',
  className,
}: EntropiaImageProps) {
  const [failedUrl, setFailedUrl] = useState<string | null>(null);
  const hasError = failedUrl === url;

  return (
    <div className={cn(styles.imageContainer, styles[size], className)}>
      {url && !hasError ? (
        <img
          src={url}
          alt={alt}
          className={styles.image}
          loading="lazy"
          onError={() => setFailedUrl(url)}
        />
      ) : (
        <span className={styles.fallback} aria-label={`${alt} indisponible`}>
          -
        </span>
      )}
    </div>
  );
}

export default EntropiaImage;
