import { useTranslations } from '@/i18n/useTranslations';
import { useFormContext, useWatch } from 'react-hook-form';
import { FormButtonsSection } from '@/shared/components';
import type { MiningSessionFormValues } from '@/shared/types/mining';
import MiningFinderSection from './MiningFinderSection';
import MiningSessionBaseSection from './MiningSessionBaseSection';
import { calculateMiningSession } from './miningSessionCalculation';
import type { MiningEquipment } from './useMiningEquipment';
import styles from './mining-session-form.module.scss';

/** Render equipment and live TT/TTC estimates, blocking submission until selection rules pass. */
export function MiningSessionFormContent({
  equipment,
  onCancel,
  pending,
}: {
  equipment: MiningEquipment;
  onCancel: () => void;
  pending: boolean;
}): import('react').JSX.Element {
  const { t } = useTranslations();
  const { control, formState } = useFormContext<MiningSessionFormValues>();
  const values = useWatch({ control }) as MiningSessionFormValues;
  const estimate = calculateMiningSession(values, equipment);
  return (
    <>
      <MiningSessionBaseSection />
      <MiningFinderSection
        equipment={equipment}
        estimate={estimate}
        selectedIds={values.finderLotIds}
      />
      <MiningFinderSection
        equipment={equipment}
        estimate={estimate}
        selectedIds={values.excavatorLotIds}
        toolRole="excavator"
      />
      <div aria-live="polite">
        <strong>
          {t('MINING.SETUP.ESTIMATE')} : {estimate.total.toFixed(2)} PED TT
          {' · '}
          {estimate.totalTtc.toFixed(2)} PED TTC
        </strong>
        <p className={styles.muted}>
          {t('MINING.SETUP.AMMO')} : {estimate.ammo.toFixed(2)} · finder :{' '}
          {estimate.finderDecay.toFixed(2)} · {t('MINING.AMPLIFIERS')} :{' '}
          {estimate.amplifierCost.toFixed(2)} PED
        </p>
        <p className={styles.muted}>{t('MINING.SETUP.DEFERRED_COST')}</p>
        {estimate.issues.map((issue) => (
          <p key={`${issue.path}:${t(issue.message)}`} className={styles.error}>
            {t(issue.message)}
          </p>
        ))}
        {Object.entries(formState.errors).map(
          ([key, error]) =>
            error?.message && (
              <p key={key} role="alert" className={styles.error}>
                {String(error.message)}
              </p>
            ),
        )}
      </div>
      <FormButtonsSection
        onCancel={onCancel}
        cancelLabel={t('TOOL_EDIT_MODAL.CANCEL')}
        submitLabel={t('MINING.SETUP.SUBMIT')}
        submitDisabled={pending || estimate.issues.length > 0}
        cancelDisabled={pending}
      />
    </>
  );
}
export default MiningSessionFormContent;
