import { useEffect } from 'react';
import type { RefObject } from 'react';

/**
 * Register dismissal handlers for an interactive component.
 *
 * @param rootRef Root element that should not trigger outside dismissal.
 * @param onDismiss Callback invoked for an outside pointer event or Escape.
 * @param enabled Whether document listeners should be registered.
 * @returns Nothing; listeners are automatically removed when disabled or unmounted.
 */
export function useDismissOnOutsideInteraction(
  rootRef: RefObject<HTMLElement | null>,
  onDismiss: () => void,
  enabled = true,
): void {
  useEffect((): (() => void) | undefined => {
    if (!enabled) return;

    const handlePointerDown = (event: PointerEvent): void => {
      if (!rootRef.current?.contains(event.target as Node)) onDismiss();
    };
    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') onDismiss();
    };

    document.addEventListener('pointerdown', handlePointerDown);
    document.addEventListener('keydown', handleKeyDown);
    return (): void => {
      document.removeEventListener('pointerdown', handlePointerDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [enabled, onDismiss, rootRef]);
}
