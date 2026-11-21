import { SidebarButtonType } from '@/shared/types';
import type { ItemStoreKind, ItemStoreRow } from '@/shared/types/listItem';

/** Return whether a catalogue row represents a stackable material or enhancer. */
export function isStackableItem(item: ItemStoreRow): boolean {
  return item.kind === 'material' || item.kind === 'enhancer';
}

/** Return whether a catalogue item is limited according to its display name. */
export function isLimitedItem(item: ItemStoreRow): boolean {
  return item.name.endsWith('(L)');
}

export function getSlidebarActiveButton(
  buttons: SidebarButtonType<string>[],
  pathname: string,
) {
  if (!pathname || !buttons || buttons.length === 0) return null;
  return buttons.find((f) => f.linkTo === pathname);
}

/** Resolve a sidebar button identifier to its catalogue store group. */
export function getItemStoreKind(buttonId: string): ItemStoreKind | undefined {
  switch (buttonId) {
    case 'finder':
      return 'finder';
    case 'excavator':
      return 'excavator';
    case 'refiner':
      return 'refiner';
    case 'finder-enhancers':
      return 'enhancer';
    case 'finder-excavators':
      return 'finder-amplifier';
    case 'materials':
      return 'material';
    default:
      return buttonId.startsWith('material-type-') ? 'material' : undefined;
  }
}
