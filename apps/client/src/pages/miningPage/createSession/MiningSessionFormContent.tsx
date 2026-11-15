import { useFormContext, useWatch } from 'react-hook-form';

import type { EnhancerResponse } from '@/api/generated/model/enhancerResponse';
import type { FinderAmplifierResponse } from '@/api/generated/model/finderAmplifierResponse';
import type { FinderResponse } from '@/api/generated/model/finderResponse';
import {
  getGetApiV1LotsUnstackableItemItemIdQueryKey,
  useGetApiV1LotsUnstackableItemItemId,
} from '@/api/generated/miningManagerAPI';
import type { MiningSessionFormValues } from '@/shared/types/mining';

import MiningFinderSection from './MiningFinderSection';
import MiningSessionBaseSection from './MiningSessionBaseSection';
import {
  getAmplifierClicks,
  getMiningDecayMultiplier,
  toPositiveNumber,
} from '../utils';

type MiningSessionFormContentProps = {
  finders: FinderResponse[];
  finderStock: Record<string, number>;
  amplifiers: FinderAmplifierResponse[];
  amplifierStock: Record<string, number>;
  enhancers: EnhancerResponse[];
  enhancerStock: Record<string, number>;
};

/** Render form sections whose values depend on the selected finder and stock. */
export function MiningSessionFormContent({
  finders,
  finderStock,
  amplifiers,
  amplifierStock,
  enhancers,
  enhancerStock,
}: MiningSessionFormContentProps) {
  const { control } = useFormContext<MiningSessionFormValues>();
  const finderItemId = useWatch({ control, name: 'finderItemId' });
  const clicks = useWatch({ control, name: 'clicks' });
  const searchType = useWatch({ control, name: 'searchType' });
  const finderLotsQuery = useGetApiV1LotsUnstackableItemItemId(finderItemId, {
    query: {
      queryKey: getGetApiV1LotsUnstackableItemItemIdQueryKey(finderItemId),
      enabled: Boolean(finderItemId),
    },
  });
  const selectedFinder = finders.find((finder) => finder.id === finderItemId);
  const selectedFinderLots = finderLotsQuery.data ?? [];
  const finderDecay = toPositiveNumber(selectedFinder?.economy.decay);
  const requiredFinderTt =
    finderDecay * getMiningDecayMultiplier(searchType) * (clicks || 0);
  const selectedFindersTt = selectedFinderLots.reduce(
    (total, lot) => total + toPositiveNumber(lot.tt),
    0,
  );
  const finderCapacityValid =
    selectedFinderLots.every((lot) => lot.tt === null) ||
    selectedFindersTt >= requiredFinderTt;
  const minimumFinderTier = selectedFinderLots.length
    ? Math.min(...selectedFinderLots.map((lot) => lot.tier ?? 0))
    : 0;

  /** Calculate amplifier clicks using the current form search mode. */
  const amplifierClicks = (amplifier: FinderAmplifierResponse) =>
    getAmplifierClicks(
      amplifier.economy.tt,
      amplifier.economy.decay,
      amplifierStock[amplifier.id] ?? 0,
      searchType,
    );

  return (
    <>
      <MiningSessionBaseSection />
      <MiningFinderSection
        finders={finders}
        finderStock={finderStock}
        finderLots={selectedFinderLots}
        selectedFinder={selectedFinder}
        requiredFinderTt={requiredFinderTt}
        selectedFindersTt={selectedFindersTt}
        finderCapacityValid={finderCapacityValid}
        amplifiers={amplifiers}
        amplifierStock={amplifierStock}
        getAmplifierClicks={amplifierClicks}
        minimumFinderTier={minimumFinderTier}
        enhancers={enhancers}
        enhancerStock={enhancerStock}
      />
    </>
  );
}

export default MiningSessionFormContent;
