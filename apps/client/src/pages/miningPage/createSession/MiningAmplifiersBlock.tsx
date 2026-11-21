import { useFormContext, useWatch } from 'react-hook-form';

import { CheckboxRHF, SubSection } from '@/shared/components';
import { useTranslations } from '@/i18n/useTranslations';
import type { FinderAmplifierResponse } from '@/api/generated/model/finderAmplifierResponse';

import type { MiningSessionFormValues } from '@/shared/types/mining';
import styles from './mining-session-form.module.scss';

type MiningAmplifiersBlockProps = {
  amplifiers: FinderAmplifierResponse[];
  stock: Record<string, number>;
  getClicksAvailable: (amplifier: FinderAmplifierResponse) => number;
};

/** Render amplifier stock, selection checkboxes, and covered-click estimates. */
export function MiningAmplifiersBlock({
  amplifiers,
  stock,
  getClicksAvailable,
}: MiningAmplifiersBlockProps): import('react').JSX.Element {
  const { t } = useTranslations();
  const { control } = useFormContext<MiningSessionFormValues>();
  const selectedAmplifierIds = useWatch({ control, name: 'amplifierIds' });

  return (
    <SubSection>
      <h3>{t('MINING.AMPLIFIERS')}</h3>
      {amplifiers.length ? (
        <div className={styles.amplifierList}>
          {amplifiers.map((amplifier): import('react').JSX.Element => (
            <div key={amplifier.id} className={styles.amplifierRow}>
              <CheckboxRHF
                name="amplifierIds"
                checkedValue={amplifier.id}
                label={amplifier.name}
              />
              <span>{stock[amplifier.id] ?? 0}</span>
              <span>{getClicksAvailable(amplifier)}</span>
            </div>
          ))}
          <p className={styles.muted}>
            {selectedAmplifierIds.length} {t('MINING.AMPLIFIERS')}
          </p>
        </div>
      ) : (
        <p className={styles.muted}>{t('MINING.NO_AMPLIFIERS')}</p>
      )}
    </SubSection>
  );
}

export default MiningAmplifiersBlock;
