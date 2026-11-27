import { useTranslations } from '@/i18n/useTranslations';
import { Section } from '@/shared/components';
import type { MiningEquipment } from './useMiningEquipment';
import MiningFindersBlock from './MiningFindersBlock';
import { MiningExcavatorsBlock } from './MiningExcavatorsBlock';
import MiningAmplifiersBlock from './MiningAmplifiersBlock';
import MiningEnhancersBlock from './MiningEnhancersBlock';
import {
  calculateMiningSession,
  minimumTier,
} from './miningSessionCalculation';
import styles from './mining-session-form.module.scss';

/** Render the equipment sections and unlock amplifier choices once a finder is selected. */
export function MiningFinderSection({
  equipment,
  estimate,
  selectedFinderIds,
  toolRole: role = 'finder',
}: {
  equipment: MiningEquipment;
  estimate: ReturnType<typeof calculateMiningSession>;
  selectedFinderIds: string[];
  toolRole?: 'finder' | 'excavator';
}): import('react').JSX.Element {
  const { t } = useTranslations();
  const selectedLots =
    role === 'finder' ? estimate.finderLots : estimate.excavatorLots;
  return (
    <Section>
      <h2>
        {role === 'finder'
          ? t('MINING.SETUP.SEARCH_SETUP')
          : t('MINING.SETUP.EXCAVATORS')}
      </h2>
      <div className={styles.finderBlocks}>
        {role === 'finder' ? (
          <MiningFindersBlock
            equipment={equipment}
            estimate={estimate}
            selectedIds={selectedFinderIds}
          />
        ) : (
          <MiningExcavatorsBlock equipment={equipment} />
        )}
        {role === 'finder' && (
          <MiningAmplifiersBlock
            equipment={equipment}
            hasFinder={Boolean(estimate.finder)}
          />
        )}
        <MiningEnhancersBlock
          equipment={equipment}
          minimumFinderTier={minimumTier(selectedLots)}
          tool={role === 'finder' ? 'FINDER' : 'EXCAVATOR'}
        />
      </div>
    </Section>
  );
}
export default MiningFinderSection;
