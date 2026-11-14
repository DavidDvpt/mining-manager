import { useTranslations } from '@/i18n/useTranslations';
import { useState } from 'react';
import { useSidebarLayoutContext } from '@/layouts/sidebarLayout';
import {
  usePostApiV1TransactionBuyStackable,
  usePostApiV1TransactionBuyUnstackable,
  usePostApiV1TransactionSellStackable,
} from '@/api/generated/miningManagerAPI';
import {
  Panel,
  Section,
  TransactionModal,
} from '@/shared/components';
import type { TransactionFormValues } from '@/shared/types/modal';
import { ItemStoreList } from '@/shared/components/itemStoreList';
import type { MaterialTypeResponse } from '@/api/generated/model/materialTypeResponse';
import { getItemStoreKind, isStackableItem } from '@/shared/utils';

import { FIXED_TRANSACTION_BUTTONS } from './constants';
import styles from './transaction-page.module.scss';
import { useItemStoreData } from '@/shared/hooks';

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
  const [selectedItem, setSelectedItem] = useState<(typeof rows.material)[number] | null>(null);
  const [transactionAction, setTransactionAction] = useState<'buy' | 'sell'>('buy');
  const buyStackable = usePostApiV1TransactionBuyStackable();
  const buyUnstackable = usePostApiV1TransactionBuyUnstackable();
  const sellStackable = usePostApiV1TransactionSellStackable();
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
      : materialType?.name ?? activeButtonId);
  const [activeViewPrefix, activeViewSuffix] = t('TRANSACTIONS.ACTIVE_VIEW').split(
    '{view}',
  );
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

  /** Submit the selected catalogue row through the action- and stackability-specific API. */
  const handleTransaction = async (values: TransactionFormValues) => {
    if (!selectedItem) return;

    if (transactionAction === 'sell') {
      if (!isStackableItem(selectedItem)) return;
      await sellStackable.mutateAsync({
        data: {
          quantity: values.quantity,
          item_id: selectedItem.id,
          tt: values.tt,
          ttc: values.ttc,
        },
      });
      return;
    }

    const kind = selectedItem.kind === 'material' ? 'material' :
      selectedItem.kind === 'enhancer' ? 'enhancer' : 'tool';
    if (isStackableItem(selectedItem)) {
      await buyStackable.mutateAsync({
        data: {
          quantity: values.quantity,
          kind,
          type_detail: 'TT',
          item_id: selectedItem.id,
          fee: values.fee,
          ttc: values.ttc,
        },
      });
      return;
    }

    await buyUnstackable.mutateAsync({
      data: {
        quantity: 1,
        tt: values.tt,
        kind,
        type_detail: 'TT',
        item_id: selectedItem.id,
        fee: values.fee,
        ttc: values.ttc,
      },
    });
  };

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
            onBuy={setSelectedItem}
            onSell={(row) => {
              setTransactionAction('sell');
              setSelectedItem(row);
            }}
          />
        ) : null}
      </Section>
      <TransactionModal
        item={selectedItem}
        lot={null}
        action={transactionAction}
        open={selectedItem !== null}
        onSubmit={handleTransaction}
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
