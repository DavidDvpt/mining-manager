import { FIXED_SIDEBAR_ITEM_BUTTONS } from '@/pages/itemPage/constants';

export type TransactionButtonId =
  | (typeof FIXED_SIDEBAR_ITEM_BUTTONS)[number]['id']
  | `material-${string}`
  | 'materials'
  | 'running-transactions';
