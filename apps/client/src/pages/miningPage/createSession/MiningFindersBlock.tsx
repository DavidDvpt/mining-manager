import { useTranslations } from '@/i18n/useTranslations';
import { useEffect, useState } from 'react';
import { useFormContext } from 'react-hook-form';
import { SubSection, EntropiaImage, SelectRHF } from '@/shared/components';
import { AppIcon } from '@/shared/components/icon';
import { getItemImageUrl } from '@/config/images';
import type { MiningSessionFormValues } from '@/shared/types/mining';
import { formatDecimalValue, formatRoundedDecimalValue } from '@/shared/utils';
import type {
  FinderResponse,
  UnstackableLotResponse,
} from '@/api/generated/model';
import {
  calculateMiningSession,
  selectUsefulFinders,
} from './miningSessionCalculation';
import type { MiningEquipment } from './useMiningEquipment';
import { toPositiveNumber } from '../utils';
import styles from './mining-session-form.module.scss';

type FinderLot = {
  item: FinderResponse;
  lot: UnstackableLotResponse;
};

/** Format a calculated PED cost to catalogue precision, with at least two decimals. */
function formatFinderCost(value: number): string {
  return formatDecimalValue(formatRoundedDecimalValue(value));
}

/** Show the model and tier on one line, with the option TT or finder depth underneath. */
function FinderIdentity({
  item,
  lot,
  optionTt,
}: FinderLot & { optionTt?: string }): import('react').JSX.Element {
  const { t } = useTranslations();
  const tier = `T${lot.tier ?? 0}`;
  return (
    <div className={styles.itemRow}>
      <div aria-hidden="true">
        <EntropiaImage url={getItemImageUrl(item.imgId)} alt="" size="small" />
      </div>
      <span>
        {item.name} · {tier}
        <br />{' '}
        <small>
          {optionTt ??
            t('MINING.SETUP.FINDER_DEPTH').replace(
              '{depth}',
              formatDecimalValue(item.details.depth),
            )}
        </small>
      </span>
    </div>
  );
}

/** List all owned finder lots and add matching limited lots in the order they will be used. */
export function MiningFindersBlock({
  equipment,
  estimate,
  selectedIds,
}: {
  equipment: MiningEquipment;
  estimate: ReturnType<typeof calculateMiningSession>;
  selectedIds: string[];
}): import('react').JSX.Element {
  const { t } = useTranslations();
  const { setValue } = useFormContext<MiningSessionFormValues>();
  const [pickerMode, setPickerMode] = useState<'hidden' | 'add' | 'replace'>(
    'hidden',
  );
  const { finder, finderLots, finderDecay, needsMoreFinderTt } = estimate;
  const options = equipment.lots.flatMap((lot) => {
    const item = equipment.finders.find((entry) => entry.id === lot.item.id);
    return item ? [{ item, lot }] : [];
  });
  useEffect(() => {
    if (!finder || finderLots.length !== selectedIds.length) return;
    const useful = selectUsefulFinders(
      finderLots,
      finderDecay,
      finder.details.isLimited,
    );
    if (useful.length < selectedIds.length) {
      setValue(
        'finderLotIds',
        useful.map((lot) => lot.id),
        {
          shouldDirty: true,
          shouldValidate: true,
        },
      );
    }
  }, [finder, finderLots, finderDecay, selectedIds, setValue]);

  /** Format the current TT for both the option content and select typeahead. */
  const renderOption = ({ item, lot }: FinderLot) => {
    const tt = formatDecimalValue(lot.tt);
    return {
      value: lot.id,
      label: `${item.name} · T${lot.tier ?? 0} · ${tt}`,
      content: <FinderIdentity item={item} lot={lot} optionTt={tt} />,
    };
  };

  const compatible = needsMoreFinderTt
    ? options.filter(
        ({ item, lot }) =>
          item.id === finder?.id &&
          !selectedIds.includes(lot.id) &&
          toPositiveNumber(lot.tt) > 0,
      )
    : [];
  const chooseLabel = t('MINING.SETUP.CHOOSE_FINDER');
  const addLabel = t('MINING.SETUP.ADD_FINDER');

  /** Remove any lot and show a replacement picker when the remaining setup needs one. */
  const removeFinder = (id: string): void => {
    const remainingIds = selectedIds.filter((selected) => selected !== id);
    setPickerMode(remainingIds.length ? 'replace' : 'hidden');
    setValue('finderLotIds', remainingIds, {
      shouldDirty: true,
      shouldValidate: true,
    });
  };

  /** Return to the add button when the supplemental dropdown closes. */
  const handlePickerOpenChange = (open: boolean): void => {
    if (!open) setPickerMode('hidden');
  };

  return (
    <SubSection>
      <h3>{t('MINING.FINDERS')}</h3>
      <div className={styles.lotList}>
        {!finder && options.length > 0 && (
          <SelectRHF
            variant="custom"
            name="finderLotIds"
            selection="replace"
            label={chooseLabel}
            trigger={chooseLabel}
            options={options.map(renderOption)}
          />
        )}
        {!options.length && (
          <p className={styles.muted}>{t('MINING.SETUP.NO_TOOLS')}</p>
        )}
        {finder &&
          finderLots.map((lot) => (
            <div key={lot.id} className={styles.finderCard}>
              <div className={styles.finderCardHeader}>
                <FinderIdentity item={finder} lot={lot} />
                <button
                  type="button"
                  className={styles.removeFinder}
                  aria-label={t('MINING.SETUP.REMOVE_FINDER').replace(
                    '{finder}',
                    `${finder.name} · T${lot.tier ?? 0}`,
                  )}
                  onClick={() => removeFinder(lot.id)}
                >
                  <AppIcon name="Trash2" size={16} aria-hidden="true" />
                </button>
              </div>
              <div className={styles.muted}>
                <div>
                  {t('MINING.SETUP.FINDER_DECAY')} ·{' '}
                  {formatFinderCost(estimate.finderDecayByLot[lot.id])} PED
                </div>
                <div>
                  {t('MINING.SETUP.AMMO')} ·{' '}
                  {formatFinderCost(estimate.finderAmmoByLot[lot.id])} PED
                </div>
              </div>
            </div>
          ))}
        {compatible.length > 0 && pickerMode === 'hidden' && (
          <button
            type="button"
            className={styles.addFinder}
            aria-label={addLabel}
            aria-haspopup="listbox"
            onClick={() => setPickerMode('add')}
          >
            <span aria-hidden="true">+</span>
          </button>
        )}
        {compatible.length > 0 && pickerMode !== 'hidden' && (
          <SelectRHF
            variant="custom"
            name="finderLotIds"
            label={addLabel}
            trigger={chooseLabel}
            options={compatible.map(renderOption)}
            selection="append"
            defaultOpen={pickerMode === 'add'}
            onOpenChange={handlePickerOpenChange}
            onSelect={() => setPickerMode('hidden')}
          />
        )}
      </div>
    </SubSection>
  );
}

export default MiningFindersBlock;
