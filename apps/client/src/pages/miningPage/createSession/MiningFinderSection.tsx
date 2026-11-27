import { useTranslations } from '@/i18n/useTranslations';
import { Section } from '@/shared/components';
import type { MiningEquipment } from './useMiningEquipment';
import type { UnstackableLotResponse } from '@/api/generated/model';
import MiningFindersBlock from './MiningFindersBlock';
import MiningAmplifiersBlock from './MiningAmplifiersBlock';
import MiningEnhancersBlock from './MiningEnhancersBlock';
import { minimumTier } from './miningSessionCalculation';
import styles from './mining-session-form.module.scss';

/** Render finder in three columns or excavators in two, with sockets shared at the lowest tier. */
export function MiningFinderSection({
  equipment,
  selectedLots,
  toolRole: role = 'finder',
}: {
  equipment: MiningEquipment;
  selectedLots: UnstackableLotResponse[];
  toolRole?: 'finder' | 'excavator';
}): import('react').JSX.Element {
  const { t } = useTranslations();
  return (
    <Section>
      <h2>
        {role === 'finder' ? t('MINING.FINDER') : t('MINING.SETUP.EXCAVATORS')}
      </h2>
      <div className={styles.finderBlocks}>
        <MiningFindersBlock equipment={equipment} toolRole={role} />
        {role === 'finder' && <MiningAmplifiersBlock equipment={equipment} />}
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
