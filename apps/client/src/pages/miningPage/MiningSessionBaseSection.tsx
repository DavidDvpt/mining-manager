import { useFormContext, useWatch } from 'react-hook-form';

import { InputRHF } from '@/shared/components';
import { Section } from '@/shared/components';
import { useTranslations } from '@/i18n/useTranslations';

import type { MiningSessionFormValues } from '@/shared/types/mining';
import styles from './mining-session-form.module.scss';

/** Render and validate the base fields of a mining-session configuration. */
export function MiningSessionBaseSection() {
  const { t } = useTranslations();
  const { register } = useFormContext<MiningSessionFormValues>();
  const planet = useWatch<MiningSessionFormValues>({ name: 'planet' });

  return (
    <Section aria-labelledby="mining-session-base-title">
      <h1 id="mining-session-base-title">{t('MINING.BASE')}</h1>
      <div className={styles.baseFields}>
        <InputRHF
          name="clicks"
          label={t('MINING.CLICKS')}
          type="number"
          min={1}
          step={1}
          className={styles.clicksInput}
        />
        <fieldset className={`${styles.fieldset} ${styles.searchTypeField}`}>
          <legend>{t('MINING.SEARCH_TYPE')}</legend>
          <div className={styles.options}>
            <div className={styles.searchTypeColumn}>
              {[
                ['E', t('MINING.ENMATTER')],
                ['O', t('MINING.ORE')],
              ].map(([value, label]) => (
                <label key={value} className={styles.option}>
                  <input
                    {...register('searchType')}
                    type="radio"
                    value={value}
                  />
                  <span>{label}</span>
                </label>
              ))}
            </div>
            <div className={styles.searchTypeColumn}>
              <label className={styles.option}>
                <input {...register('searchType')} type="radio" value="OE" />
                <span>{t('MINING.ORE_ENMATTER')}</span>
              </label>
            </div>
          </div>
        </fieldset>
        <InputRHF
          name="planet"
          label={t('MINING.PLANET')}
          required
          className={styles.wideInput}
        />
        <InputRHF
          name="zone"
          label={t('MINING.ZONE')}
          disabled={!String(planet ?? '').trim()}
          className={styles.wideInput}
        />
      </div>
    </Section>
  );
}

export default MiningSessionBaseSection;
