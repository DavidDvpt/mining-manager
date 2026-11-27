import { useTranslations } from '@/i18n/useTranslations';
import { useEffect } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';
import {
  CheckboxRHF,
  SelectRHF,
  SubSection,
  EntropiaImage,
} from '@/shared/components';
import { getItemImageUrl } from '@/config/images';
import type { MiningSessionFormValues } from '@/shared/types/mining';
import type { MiningEquipment } from './useMiningEquipment';
import {
  calculateMiningSession,
  selectUsefulFinders,
} from './miningSessionCalculation';
import styles from './mining-session-form.module.scss';

type Props = { equipment: MiningEquipment; toolRole: 'finder' | 'excavator' };

/** Offer additional finders only until capacity is covered and display each lot’s allocated decay. */
export function MiningFindersBlock({
  equipment,
  toolRole: role,
}: Props): import('react').JSX.Element {
  const { t } = useTranslations();
  const { control, setValue } = useFormContext<MiningSessionFormValues>();
  const values = useWatch({ control }) as MiningSessionFormValues;
  const field = role === 'finder' ? 'finderLotIds' : 'excavatorLotIds';
  const tools = role === 'finder' ? equipment.finders : equipment.excavators;
  const allLots = equipment.lots.filter(
    (lot) =>
      tools.some((item) => item.id === lot.item.id) &&
      (role !== 'finder' || lot.item.id === values.finderItemId),
  );
  useEffect(() => {
    if (role === 'finder')
      setValue('finderLotIds', [], { shouldValidate: true });
  }, [values.finderItemId, role, setValue]);
  const estimate = calculateMiningSession(values, equipment);
  const finder = estimate.finder;
  useEffect(() => {
    if (role !== 'finder' || !finder) return;
    const selectedLots = values.finderLotIds.flatMap((id) =>
      allLots.filter((lot) => lot.id === id),
    );
    const useful = selectUsefulFinders(
      selectedLots,
      estimate.finderDecay,
      finder.details.isLimited,
    ).map((lot) => lot.id);
    if (useful.join(',') !== values.finderLotIds.join(','))
      setValue('finderLotIds', useful, { shouldValidate: true });
  }, [
    role,
    finder,
    values.finderLotIds,
    allLots,
    estimate.finderDecay,
    setValue,
  ]);
  const covered =
    estimate.finderLots.length > 0 &&
    (!finder?.details.isLimited ||
      !estimate.issues.some(
        (issue) => issue.message === 'MINING.SETUP.FINDER_CAPACITY',
      ));
  const lots = allLots
    .filter(
      (lot) =>
        role !== 'finder' || values.finderLotIds.includes(lot.id) || !covered,
    )
    .sort(
      (a, b) =>
        Number(a.tt ?? 0) - Number(b.tt ?? 0) || a.id.localeCompare(b.id),
    );
  /** Prefer a newly chosen sufficient finder and retain additional L lots only while needed. */
  const selectFinder = (id: string, checked: boolean): void => {
    if (!finder) return;
    const ids = checked
      ? [id, ...values.finderLotIds.filter((value) => value !== id)]
      : values.finderLotIds.filter((value) => value !== id);
    const selected = ids.flatMap((value) =>
      allLots.filter((lot) => lot.id === value),
    );
    setValue(
      'finderLotIds',
      selectUsefulFinders(
        selected,
        estimate.finderDecay,
        finder.details.isLimited,
      ).map((lot) => lot.id),
      { shouldDirty: true, shouldValidate: true },
    );
  };
  return (
    <SubSection>
      <h3>
        {role === 'finder' ? t('MINING.FINDERS') : t('MINING.SETUP.EXCAVATORS')}
      </h3>
      {role === 'finder' && (
        <SelectRHF
          name="finderItemId"
          label={t('MINING.SETUP.FINDER_MODEL')}
          options={[
            { value: '', label: t('MINING.SETUP.CHOOSE_FINDER') },
            ...tools.map((item) => ({ value: item.id, label: item.name })),
          ]}
        />
      )}
      <div className={styles.lotList}>
        {lots.map((lot) => {
          const item = tools.find((tool) => tool.id === lot.item.id);
          if (!item) return null;
          const decay = estimate.finderDecayByLot[lot.id] ?? 0;
          return (
            <div key={lot.id} className={styles.itemRow}>
              <EntropiaImage
                url={getItemImageUrl(item.imgId)}
                alt={item.name}
                size="small"
              />
              <div>
                <CheckboxRHF
                  name={field}
                  onCheckedChange={
                    role === 'finder'
                      ? (checked) => selectFinder(lot.id, checked)
                      : undefined
                  }
                  checkedValue={lot.id}
                  label={`${item.name} · T${lot.tier ?? 0}`}
                />
                <small>
                  {item.details.isLimited
                    ? `${lot.tt ?? '—'} TT · L`
                    : t('MINING.SETUP.REPAIRABLE')}
                </small>
                <p className={styles.muted}>
                  {role === 'finder'
                    ? `${decay.toFixed(2)} ${t('MINING.SETUP.DECAY_COST')}`
                    : t('MINING.SETUP.CLOSING_COST')}
                </p>
              </div>
            </div>
          );
        })}
      </div>
      {!lots.length && (
        <p className={styles.muted}>{t('MINING.SETUP.NO_TOOLS')}</p>
      )}
      {role === 'finder' && estimate.finder && (
        <p
          className={
            estimate.issues.some((issue) => issue.path === 'finderLotIds')
              ? styles.error
              : styles.muted
          }
        >
          {t('MINING.SETUP.FINDER_TT')} : {estimate.finderTt.toFixed(2)} · decay
          : {estimate.finderDecay.toFixed(2)} PED
          <br />
          {t('MINING.SETUP.AMMO')} : {estimate.ammo.toFixed(2)} PED
        </p>
      )}
    </SubSection>
  );
}
export default MiningFindersBlock;
