import { Section } from '@/shared/components';
import { useTranslations } from '@/i18n/useTranslations';
import type { EnhancerResponse } from '@/api/generated/model/enhancerResponse';
import type { FinderAmplifierResponse } from '@/api/generated/model/finderAmplifierResponse';
import type { FinderResponse } from '@/api/generated/model/finderResponse';
import type { UnstackableLotResponse } from '@/api/generated/model/unstackableLotResponse';

import MiningAmplifiersBlock from './MiningAmplifiersBlock';
import MiningEnhancersBlock from './MiningEnhancersBlock';
import MiningFindersBlock from './MiningFindersBlock';
import styles from './mining-session-form.module.scss';

type MiningFinderSectionProps = {
  finders: FinderResponse[];
  finderStock: Record<string, number>;
  finderLots: UnstackableLotResponse[];
  selectedFinder?: FinderResponse;
  requiredFinderTt: number;
  selectedFindersTt: number;
  finderCapacityValid: boolean;
  amplifiers: FinderAmplifierResponse[];
  amplifierStock: Record<string, number>;
  getAmplifierClicks: (amplifier: FinderAmplifierResponse) => number;
  minimumFinderTier: number;
  enhancers: EnhancerResponse[];
  enhancerStock: Record<string, number>;
};

/** Render the finder section and its three independent horizontal blocks. */
export function MiningFinderSection({
  finders,
  finderStock,
  finderLots,
  selectedFinder,
  requiredFinderTt,
  selectedFindersTt,
  finderCapacityValid,
  amplifiers,
  amplifierStock,
  getAmplifierClicks,
  minimumFinderTier,
  enhancers,
  enhancerStock,
}: MiningFinderSectionProps): import('react').JSX.Element {
  const { t } = useTranslations();

  return (
    <Section aria-labelledby="mining-session-finder-title">
      <h2 id="mining-session-finder-title">{t('MINING.FINDER')}</h2>
      <div className={styles.finderBlocks}>
        <MiningFindersBlock
          finders={finders}
          stock={finderStock}
          lots={finderLots}
          selectedFinder={selectedFinder}
          requiredTt={requiredFinderTt}
          selectedTt={selectedFindersTt}
          isCapacityValid={finderCapacityValid}
        />
        <MiningAmplifiersBlock
          amplifiers={amplifiers}
          stock={amplifierStock}
          getClicksAvailable={getAmplifierClicks}
        />
        <MiningEnhancersBlock
          minimumFinderTier={minimumFinderTier}
          enhancers={enhancers}
          stock={enhancerStock}
        />
      </div>
    </Section>
  );
}

export default MiningFinderSection;
