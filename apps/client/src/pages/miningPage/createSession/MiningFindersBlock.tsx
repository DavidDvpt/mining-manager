import { useTranslations } from '@/i18n/useTranslations';
import { useEffect } from 'react';
import { useFormContext } from 'react-hook-form';
import type { MiningSessionFormValues } from '@/shared/types/mining';
import {
  formatDecimalValue,
  formatRoundedDecimalValue,
  parseNumber,
} from '@/shared/utils';
import {
  calculateMiningSession,
  selectUsefulFinders,
} from './miningSessionCalculation';
import type { MiningEquipment } from './useMiningEquipment';
import { toPositiveNumber } from '../utils';
import { MiningToolLots } from './MiningToolLots';

const finderDepthFormat = new Intl.NumberFormat('fr-FR', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
  useGrouping: false,
});

/** Format a calculated PED cost to catalogue precision, with at least two decimals. */
function formatFinderCost(value: number): string {
  return formatDecimalValue(formatRoundedDecimalValue(value));
}

/** List owned finder lots, display their estimated depth, and add matching limited lots in usage order. */
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

  const compatible = needsMoreFinderTt
    ? options.filter(
        ({ item, lot }) =>
          item.id === finder?.id &&
          !selectedIds.includes(lot.id) &&
          toPositiveNumber(lot.tt) > 0,
      )
    : [];
  const depth =
    estimate.enhancedFinderDepth ?? parseNumber(finder?.details.depth);

  return (
    <MiningToolLots
      field="finderLotIds"
      title={t('MINING.FINDERS')}
      chooseLabel={t('MINING.SETUP.CHOOSE_FINDER')}
      addLabel={t('MINING.SETUP.ADD_FINDER')}
      options={options}
      selectedIds={selectedIds}
      additionalOptions={compatible}
      selected={
        finder
          ? finderLots.map((lot) => ({
              item: finder,
              lot,
              subtitle: t('MINING.SETUP.FINDER_DEPTH').replace(
                '{depth}',
                depth === null ? '—' : finderDepthFormat.format(depth),
              ),
              highlight: estimate.enhancedFinderDepth !== null,
              details: (
                <>
                  <div>
                    {t('MINING.SETUP.FINDER_DECAY')} ·{' '}
                    {formatFinderCost(estimate.finderDecayByLot[lot.id])} PED
                  </div>
                  <div>
                    {t('MINING.SETUP.AMMO')} ·{' '}
                    {formatFinderCost(estimate.finderAmmoByLot[lot.id])} PED
                  </div>
                </>
              ),
            }))
          : []
      }
    />
  );
}

export default MiningFindersBlock;
