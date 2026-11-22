import { useTranslations } from '@/i18n/useTranslations';
import { Outlet, useNavigate } from 'react-router-dom';
import { Panel, Section } from '@/shared/components';
import { Switch } from '@/components/ui/switch';
import { ItemList } from './itemList';

import styles from './item-list-layout.module.scss';
import { useItemStoreData } from '@/shared/hooks';
import { JSX, useMemo, useState } from 'react';
import { ItemKind, ItemSubKind } from '@/router/constants';

import { ItemRow } from '@/shared';
import { toSlug } from '@/shared/utils/string';

interface ItemListLayoutProps {
  kind: ItemKind;
  subKind?: ItemSubKind;
}

export function ItemPageContent({
  kind,
  subKind,
}: ItemListLayoutProps): JSX.Element {
  const navigate = useNavigate();
  const { t } = useTranslations();
  const [ownedOnly, setOwnedOnly] = useState(false);
  const { rows, isLoading, isError } = useItemStoreData();

  const [activeViewPrefix, activeViewSuffix] = t(
    'TRANSACTIONS.ACTIVE_VIEW',
  ).split('{view}');

  const filteredRows = useMemo((): ItemRow[] => {
    if (kind !== 'material' || !subKind) {
      return rows[kind] ?? [];
    }

    return (
      rows[kind]?.filter((row): boolean => {
        return kind === 'material' && subKind
          ? row.kind === 'material' &&
              toSlug(row.details.type.name) === toSlug(subKind)
          : true;
      }) ?? []
    );
  }, [rows, kind, subKind]);

  const visibleRows = ownedOnly
    ? filteredRows.filter((row) => (row.stock ?? 0) > 0)
    : filteredRows;

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

        <ItemList
          kind={kind}
          rows={visibleRows}
          isLoading={isLoading}
          isError={isError}
          showMaterialType={kind === 'material'}
          onBuy={(row) => navigate(`${row.id}/buy?item=${JSON.stringify(row)}`)}
          onSell={(row) =>
            navigate(`${row.id}/sell?item=${JSON.stringify(row)}`)
          }
          onEdit={(row) =>
            navigate(`${row.id}/edit?item=${JSON.stringify(row)}`)
          }
        />
      </Section>
      <Outlet />
    </Panel>
  );
}

export default ItemPageContent;
