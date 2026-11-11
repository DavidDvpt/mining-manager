import { useTranslations } from '@/i18n/useTranslations';
import { useSidebarLayoutContext } from '@/layouts/sidebarLayout';
import { Panel, Section } from '@/shared/components';
import { ItemStoreList } from '@/shared/components/itemStoreList';
import type { ItemStoreKind } from '@/shared/types/listItem';
import type { MaterialTypeResponse } from '@/api/generated/model/materialTypeResponse';

import { FIXED_TRANSACTION_BUTTONS } from './constants';
import styles from './transaction-page.module.scss';
import { useItemStoreData } from '@/shared/hooks';

type TransactionContentProps = {
  materialTypes?: MaterialTypeResponse[];
};

/** Resolve the active sidebar button to the catalogue group shown in the store list. */
function getItemStoreKind(buttonId: string): ItemStoreKind | undefined {
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

/** Render transaction content using the sidebar selection and loaded material types. */
export function TransactionContent({
  materialTypes = [],
}: TransactionContentProps) {
  const { activeButtonId } = useSidebarLayoutContext();
  const { t } = useTranslations();
  const { rows, isLoading, isError } = useItemStoreData();
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
          />
        ) : null}
      </Section>
    </Panel>
  );
}

export default TransactionContent;
