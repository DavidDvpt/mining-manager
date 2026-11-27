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

/** Render the selected equipment role with its common enhancer sockets and finder-only amplifiers. */
export function MiningFinderSection({
  equipment,
  estimate,
  selectedIds,
  toolRole: role = 'finder',
}: {
  equipment: MiningEquipment;
  estimate: ReturnType<typeof calculateMiningSession>;
  selectedIds: string[];
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
          : t('MINING.SETUP.EXCAVATION')}
      </h2>
      <div className={styles.finderBlocks}>
        {role === 'finder' ? (
          <MiningFindersBlock
            equipment={equipment}
            estimate={estimate}
            selectedIds={selectedIds}
          />
        ) : (
          <MiningExcavatorsBlock
            equipment={equipment}
            selectedIds={selectedIds}
          />
        )}
        {role === 'finder' && (
          <MiningAmplifiersBlock
            equipment={equipment}
            hasFinder={Boolean(estimate.finder)}
          />
        )}
        <MiningEnhancersBlock
          equipment={equipment}
          minimumToolTier={minimumTier(selectedLots)}
          tool={role === 'finder' ? 'FINDER' : 'EXCAVATOR'}
        />
      </div>
    </Section>
  );
}
export default MiningFinderSection;
