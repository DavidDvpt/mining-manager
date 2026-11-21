import type { LucideIcon, LucideProps } from 'lucide-react';
import {
  ChartNoAxesCombined,
  Check,
  ChevronDown,
  ChevronUp,
  CornerDownLeft,
  EllipsisVertical,
  Eye,
  EyeOff,
  FlaskConical,
  HandCoins,
  Pencil,
  RefreshCw,
  Save,
  ShoppingCart,
  Trash2,
  X,
} from 'lucide-react';

/** Names of the Lucide icons exposed by the shared icon component. */
export const AppIconName = {
  ChartNoAxesCombined: 'ChartNoAxesCombined',
  Check: 'Check',
  ChevronDown: 'ChevronDown',
  ChevronUp: 'ChevronUp',
  CornerDownLeft: 'CornerDownLeft',
  EllipsisVertical: 'EllipsisVertical',
  Eye: 'Eye',
  EyeOff: 'EyeOff',
  FlaskConical: 'FlaskConical',
  HandCoins: 'HandCoins',
  Pencil: 'Pencil',
  RefreshCw: 'RefreshCw',
  Save: 'Save',
  ShoppingCart: 'ShoppingCart',
  Trash2: 'Trash2',
  X: 'X',
} as const;

export type AppIconName = (typeof AppIconName)[keyof typeof AppIconName];

const icons: Record<AppIconName, LucideIcon> = {
  [AppIconName.ChartNoAxesCombined]: ChartNoAxesCombined,
  [AppIconName.Check]: Check,
  [AppIconName.ChevronDown]: ChevronDown,
  [AppIconName.ChevronUp]: ChevronUp,
  [AppIconName.CornerDownLeft]: CornerDownLeft,
  [AppIconName.EllipsisVertical]: EllipsisVertical,
  [AppIconName.Eye]: Eye,
  [AppIconName.EyeOff]: EyeOff,
  [AppIconName.FlaskConical]: FlaskConical,
  [AppIconName.HandCoins]: HandCoins,
  [AppIconName.Pencil]: Pencil,
  [AppIconName.RefreshCw]: RefreshCw,
  [AppIconName.Save]: Save,
  [AppIconName.ShoppingCart]: ShoppingCart,
  [AppIconName.Trash2]: Trash2,
  [AppIconName.X]: X,
};

export type AppIconProps = Omit<LucideProps, 'ref'> & {
  name: AppIconName;
};

/** Render one centrally registered Lucide icon selected by its public name. */
export function AppIcon({
  name,
  ...props
}: AppIconProps): import('react').JSX.Element {
  const Icon = icons[name];

  return <Icon {...props} />;
}

export default AppIcon;
