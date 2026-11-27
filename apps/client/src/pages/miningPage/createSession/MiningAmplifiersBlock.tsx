import { useTranslations } from '@/i18n/useTranslations';
import { useFormContext, useWatch } from 'react-hook-form';
import { SubSection, EntropiaImage } from '@/shared/components';
import { RadioRHF, RadioRHFItem } from '@/shared/components/form/RadioRHF';
import { getItemImageUrl } from '@/config/images';
import type { MiningSessionFormValues } from '@/shared/types/mining';
import { getAmplifierClicks, getMiningDecayMultiplier } from '../utils';
import type { MiningEquipment } from './useMiningEquipment';
import styles from './mining-session-form.module.scss';

/** Show amplifier choices, click capacity, and cost or stock error once a finder is selected. */
export function MiningAmplifiersBlock({
  equipment,
  hasFinder,
}: {
  equipment: MiningEquipment;
  hasFinder: boolean;
}): import('react').JSX.Element {
  const { t } = useTranslations();
  const { control } = useFormContext<MiningSessionFormValues>();
  const values = useWatch({ control }) as MiningSessionFormValues;
  if (!hasFinder) {
    return (
      <SubSection>
        <h3>{t('MINING.AMPLIFIERS')}</h3>
        <p className={styles.muted}>{t('MINING.SETUP.AMP_REQUIRES_FINDER')}</p>
      </SubSection>
    );
  }
  return (
    <SubSection>
      <h3>{t('MINING.AMPLIFIERS')}</h3>
      <RadioRHF
        name="amplifierItemId"
        aria-label={t('MINING.SETUP.AMP_MODEL')}
        className={styles.lotList}
      >
        <RadioRHFItem value="" className={styles.itemRow}>
          <span>{t('MINING.SETUP.NO_AMP')}</span>
        </RadioRHFItem>
        {equipment.amplifiers.map((item) => {
          const lots = equipment.lots.filter((lot) => lot.item.id === item.id);
          const capacity = item.details.isLimited
            ? lots.reduce(
                (sum, lot) =>
                  sum +
                  getAmplifierClicks(
                    lot.tt,
                    item.economy.decay,
                    1,
                    values.searchType,
                  ),
                0,
              )
            : Infinity;
          const cost =
            values.amplifierItemId === item.id
              ? values.clicks *
                getMiningDecayMultiplier(values.searchType) *
                Number(item.economy.decay ?? 0)
              : 0;
          return (
            <RadioRHFItem
              key={item.id}
              value={item.id}
              className={styles.itemRow}
            >
              <EntropiaImage
                url={getItemImageUrl(item.imgId)}
                alt={item.name}
                size="small"
              />
              <span>
                {item.name}
                <br />
                <small>
                  {lots.length} {t('MINING.SETUP.AVAILABLE')} ·{' '}
                  {Number.isFinite(capacity) ? capacity : '∞'}{' '}
                  {t('MINING.SETUP.CLICKS')}
                </small>
                <br />
                {capacity < values.clicks ? (
                  <small className={styles.error}>
                    {t('MINING.SETUP.AMP_INSUFFICIENT_QUANTITY')}
                  </small>
                ) : (
                  <small>
                    {cost.toFixed(2)} {t('MINING.SETUP.SESSION_COST')}
                  </small>
                )}
              </span>
            </RadioRHFItem>
          );
        })}
      </RadioRHF>
    </SubSection>
  );
}
export default MiningAmplifiersBlock;
