import { useFormContext, useWatch } from 'react-hook-form';

import { CheckboxRHF, SelectRHF, SubSection } from '@/shared/components';
import { useTranslations } from '@/i18n/useTranslations';
import type { FinderResponse } from '@/api/generated/model/finderResponse';
import type { UnstackableLotResponse } from '@/api/generated/model/unstackableLotResponse';

import type { MiningSessionFormValues } from '@/shared/types/mining';
import styles from './mining-session-form.module.scss';

type MiningFindersBlockProps = {
  finders: FinderResponse[];
  stock: Record<string, number>;
  lots: UnstackableLotResponse[];
  selectedFinder?: FinderResponse;
  requiredTt: number;
  selectedTt: number;
  isCapacityValid: boolean;
};

/** Render finder model and owned-lot selection with its TT capacity feedback. */
export function MiningFindersBlock({
  finders,
  stock,
  lots,
  selectedFinder,
  requiredTt,
  selectedTt,
  isCapacityValid,
}: MiningFindersBlockProps) {
  const { t } = useTranslations();
  const { control } = useFormContext<MiningSessionFormValues>();
  const selectedLotIds = useWatch({ control, name: 'finderLotIds' });

  return (
    <SubSection>
      <h3>{t('MINING.FINDERS')}</h3>
      {finders.length ? (
        <>
          <SelectRHF
            name="finderItemId"
            label={t('MINING.SELECT_FINDER')}
            options={finders.map((finder) => ({
              value: finder.id,
              label: `${finder.name} · ${stock[finder.id] ?? 0}`,
            }))}
          />
          <div className={styles.lotList}>
            {lots.map((lot) => (
              <CheckboxRHF
                key={lot.id}
                name="finderLotIds"
                checkedValue={lot.id}
                label={`${selectedFinder?.name ?? ''} · T${lot.tier ?? '—'} · ${lot.tt ?? '—'} TT`}
              />
            ))}
          </div>
          <p className={isCapacityValid ? styles.muted : styles.error}>
            {t('MINING.FINDER_TT')}: {selectedTt.toFixed(2)} /{' '}
            {requiredTt.toFixed(2)} TT
          </p>
          {!selectedLotIds.length ? (
            <p className={styles.error}>{t('MINING.SELECT_FINDER')}</p>
          ) : null}
        </>
      ) : (
        <p className={styles.muted}>{t('MINING.NO_FINDERS')}</p>
      )}
    </SubSection>
  );
}

export default MiningFindersBlock;
