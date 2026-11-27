import { useTranslations } from '@/i18n/useTranslations';
import { Section } from '@/shared/components';
import type { MiningEquipment } from './useMiningEquipment';
import MiningFindersBlock from './MiningFindersBlock';
import { MiningExcavatorsBlock } from './MiningExcavatorsBlock';
import MiningAmplifiersBlock from './MiningAmplifiersBlock';
import MiningEnhancersBlock from './MiningEnhancersBlock';
import type { calculateMiningSession } from './miningSessionCalculation';
import styles from './mining-session-form.module.scss';

/** Render the equipment section with the socket tier calculated for its tool role. */
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
          socketTier={
            role === 'finder'
              ? estimate.finderSocketTier
              : estimate.excavatorSocketTier
          }
          tool={role === 'finder' ? 'FINDER' : 'EXCAVATOR'}
        />
      </div>
    </Section>
  );
}
export default MiningFinderSection;
