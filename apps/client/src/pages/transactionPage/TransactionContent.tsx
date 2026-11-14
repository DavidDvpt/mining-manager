import { useTranslations } from '@/i18n/useTranslations';
import { useEffect } from 'react';
import { useSidebarLayoutContext } from '@/layouts/sidebarLayout';
import { Panel, Section, TransactionModal } from '@/shared/components';
import { ItemStoreList } from './itemStoreList';
import type { MaterialTypeResponse } from '@/api/generated/model/materialTypeResponse';
import { getItemStoreKind, isStackableItem } from '@/shared/utils';

import { FIXED_TRANSACTION_BUTTONS } from './constants';
import styles from './transaction-page.module.scss';
import { useItemStoreData } from '@/shared/hooks';
import {
  getGetApiV1LotsUnstackableItemItemIdQueryKey,
  useGetApiV1LotsUnstackableItemItemId,
} from '@/api/generated/miningManagerAPI';
import type {
  TransactionContext,
  TransactionContextUpdate,
} from './transactionContext';

type TransactionContentProps = {
  materialTypes?: MaterialTypeResponse[];
  context: TransactionContext;
  updateContext: (updates: TransactionContextUpdate) => void;
};

/** Render transaction content using the sidebar selection and loaded material types. */
export function TransactionContent({
  materialTypes = [],
  context,
  updateContext,
}: TransactionContentProps) {
  const { activeButtonId } = useSidebarLayoutContext();
  const { t } = useTranslations();
  const { rows, isLoading, isError } = useItemStoreData();
  const selectedItem =
    Object.values(rows)
      .flat()
      .find((row) => row.id === context.item_id) ?? null;
  const selectedItemId = context.item_id ?? '';
  const unstackableLots = useGetApiV1LotsUnstackableItemItemId(selectedItemId, {
    query: {
      queryKey: getGetApiV1LotsUnstackableItemItemIdQueryKey(selectedItemId),
      enabled:
        context.type === 'sell' &&
        selectedItem !== null &&
        !isStackableItem(selectedItem),
    },
  });
  const selectedLot =
    unstackableLots.data?.find(({ id }) => id === context.lot_id) ??
    unstackableLots.data?.[0] ??
    null;

  useEffect(() => {
    if (
      context.type === 'sell' &&
      selectedItem &&
      !isStackableItem(selectedItem) &&
      selectedLot &&
      !context.lot_id
    ) {
      updateContext({ lot_id: selectedLot.id });
    }
  }, [context.lot_id, context.type, selectedItem, selectedLot, updateContext]);
  const fixedButton = FIXED_TRANSACTION_BUTTONS.find(
    ({ id }) => id === activeButtonId,
  );
  const materialType = materialTypes.find(
    ({ id }) => `material-type-${id}` === activeButtonId,
  );
  const activeView =
    fixedButton?.label ??
    (activeButtonId === 'materials'
      ? t('TRANSACTIONS.MATERIALS')
      : activeButtonId === 'running-transactions'
        ? t('TRANSACTIONS.RUNNING_TRANSACTIONS')
        : (materialType?.name ?? activeButtonId));
  const [activeViewPrefix, activeViewSuffix] = t(
    'TRANSACTIONS.ACTIVE_VIEW',
  ).split('{view}');
  const activeKind = getItemStoreKind(activeButtonId);
  const visibleRows = activeKind
    ? rows[activeKind].filter(
        (row) =>
          !activeButtonId.startsWith('material-type-') ||
          row.details.type === materialType?.id,
      )
    : [];
  const displayRows =
    activeKind === 'material'
      ? visibleRows.map((row) => ({
          ...row,
          details: {
            ...row.details,
            type:
              materialTypes.find(({ id }) => id === row.details.type)?.name ??
              row.details.type,
          },
        }))
      : visibleRows;

  return (
    <Panel className={styles.page}>
      <Section>
        <h1>{t('TRANSACTIONS.TITLE')}</h1>
        <p>
          {activeViewPrefix}
          <span className={styles.activeView}>{activeView}</span>
          {activeViewSuffix}
        </p>
        <p>{t('TRANSACTIONS.DESCRIPTION')}</p>
        {activeKind ? (
          <ItemStoreList
            kind={activeKind}
            rows={displayRows}
            isLoading={isLoading}
            isError={isError}
            showMaterialType={activeButtonId === 'materials'}
            onBuy={(row) => {
              updateContext({ type: 'buy', item_id: row.id, lot_id: null });
            }}
            onSell={(row) => {
              updateContext({ type: 'sell', item_id: row.id, lot_id: null });
            }}
          />
        ) : null}
      </Section>
      <TransactionModal
        item={selectedItem}
        lot={selectedLot}
        lots={unstackableLots.data ?? []}
        action={context.type ?? 'buy'}
        open={
          selectedItem !== null &&
          context.type !== undefined &&
          (context.type === 'buy' ||
            isStackableItem(selectedItem) ||
            Boolean(unstackableLots.data?.length))
        }
        onOpenChange={(open) => {
          if (!open) {
            updateContext({ type: null, item_id: null, lot_id: null });
          }
        }}
      />
    </Panel>
  );
}

export default TransactionContent;
