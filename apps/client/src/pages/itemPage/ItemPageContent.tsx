import { useTranslations } from '@/i18n/useTranslations';
import { Outlet } from 'react-router-dom';
import { Panel, Section } from '@/shared/components';
import { Switch } from '@/components/ui/switch';
import { ItemStoreList } from './itemStoreList';

import styles from './item-list-layout.module.scss';
import { useItemStoreData } from '@/shared/hooks';
import { useMemo, useState } from 'react';
import { ItemKind, ItemSubKind } from '@/router/constants';
import { toSlug } from '@/shared/utils/string';

interface ItemListLayoutProps {
  kind: ItemKind;
  subKind?: ItemSubKind;
}

export function ItemPageContent({
  kind,
  subKind,
}: ItemListLayoutProps): import('react').JSX.Element {
  const { t } = useTranslations();
  const [ownedOnly, setOwnedOnly] = useState(true);
  const { rows, isLoading, isError } = useItemStoreData();

  console.log(rows);
  const [activeViewPrefix, activeViewSuffix] = t(
    'TRANSACTIONS.ACTIVE_VIEW',
  ).split('{view}');

  const visibleRows = useMemo((): import('../../shared').ItemStoreRow[] => {
    if (kind !== 'material' || !subKind) {
      return rows[kind] ?? [];
    }

    return (
      rows[kind]?.filter((row): boolean =>
        kind === 'material' && subKind
          ? row.kind === 'material' && row.details.type.name === toSlug(subKind)
          : true,
      ) ?? []
    );
  }, [rows, kind, subKind]);

  // const ownedRows = ownedOnly
  //   ? visibleRows.filter((row) => (row.stock ?? 0) > 0)
  //   : visibleRows;
  // const displayRows =
  //   activeKind === 'material'
  //     ? ownedRows.map((row) => ({
  //         ...row,
  //         details: {
  //           ...row.details,
  //           type:
  //             materialTypes.find(({ id }) => id === row.details.type)?.name ??
  //             row.details.type,
  //         },
  //       }))
  //     : ownedRows;

  return (
    <Panel className={styles.page}>
      <Section className={styles.content}>
        <h1>{t('TRANSACTIONS.TITLE')}</h1>
        <p>
          {activeViewPrefix}
          <span className={styles.activeView}>{kind}</span>
          {activeViewSuffix}
        </p>
        <p>{t('TRANSACTIONS.DESCRIPTION')}</p>
        <div className={styles.ownedFilter}>
          <span>{t('TRANSACTIONS.OWNED_ONLY')}</span>
          <Switch
            checked={ownedOnly}
            onCheckedChange={setOwnedOnly}
            aria-label={t('TRANSACTIONS.OWNED_ONLY')}
          />
        </div>

        <ItemStoreList
          kind={kind}
          rows={visibleRows}
          isLoading={isLoading}
          isError={isError}
          showMaterialType={kind === 'material'}
        />
      </Section>
      <Outlet />
    </Panel>
  );
}

export default ItemPageContent;
