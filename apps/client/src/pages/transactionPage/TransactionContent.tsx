import { useTranslations } from '@/i18n/useTranslations';
import { useState } from 'react';
import { useSidebarLayoutContext } from '@/layouts/sidebarLayout';
import { Panel, Section, TransactionModal } from '@/shared/components';
import { ItemStoreList } from './itemStoreList';
import type { MaterialTypeResponse } from '@/api/generated/model/materialTypeResponse';
import { getItemStoreKind } from '@/shared/utils';

import { FIXED_TRANSACTION_BUTTONS } from './constants';
import styles from './transaction-page.module.scss';
import { useItemStoreData } from '@/shared/hooks';
import {
  getGetApiV1LotsUnstackableItemItemIdQueryKey,
  useGetApiV1LotsUnstackableItemItemId,
} from '@/api/generated/miningManagerAPI';

type TransactionContentProps = {
  materialTypes?: MaterialTypeResponse[];
};

/** Render transaction content using the sidebar selection and loaded material types. */
export function TransactionContent({
  materialTypes = [],
}: TransactionContentProps) {
  const { activeButtonId } = useSidebarLayoutContext();
  const { t } = useTranslations();
  const { rows, isLoading, isError } = useItemStoreData();
  const [selectedItem, setSelectedItem] = useState<
    (typeof rows.material)[number] | null
  >(null);
  const [transactionAction, setTransactionAction] = useState<'buy' | 'sell'>(
    'buy',
  );
  const selectedItemId = selectedItem?.id ?? '';
  const unstackableLots = useGetApiV1LotsUnstackableItemItemId(selectedItemId, {
    query: {
      queryKey: getGetApiV1LotsUnstackableItemItemIdQueryKey(selectedItemId),
      enabled: transactionAction === 'sell' && selectedItem !== null,
    },
  });
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
              setTransactionAction('buy');
              setSelectedItem(row);
            }}
            onSell={(row) => {
              setTransactionAction('sell');
              setSelectedItem(row);
            }}
          />
        ) : null}
      </Section>
      <TransactionModal
        item={selectedItem}
        lot={unstackableLots.data?.[0] ?? null}
        lots={unstackableLots.data ?? []}
        action={transactionAction}
        open={
          selectedItem !== null &&
          (transactionAction === 'buy' || Boolean(unstackableLots.data?.[0]))
        }
        onOpenChange={(open) => {
          if (!open) {
            setSelectedItem(null);
            setTransactionAction('buy');
          }
        }}
      />
    </Panel>
  );
}

export default TransactionContent;
