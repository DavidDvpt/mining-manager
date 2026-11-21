import { useEffect } from 'react';
import { useController, useFormContext, useWatch } from 'react-hook-form';

import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import {
  getGetApiV1PlanetPlanetIdZoneQueryKey,
  useGetApiV1Planet,
  useGetApiV1PlanetPlanetIdZone,
} from '@/api/generated/miningManagerAPI';
import { ComboboxRHF, InputRHF, SelectRHF, Section } from '@/shared/components';
import { useTranslations } from '@/i18n/useTranslations';

import type { MiningSessionFormValues } from '@/shared/types/mining';
import styles from './mining-session-form.module.scss';

/** Render and validate the base fields of a mining-session configuration. */
export function MiningSessionBaseSection(): import('react').JSX.Element {
  const { t } = useTranslations();
  const { control, setValue } = useFormContext<MiningSessionFormValues>();
  const planet = useWatch<MiningSessionFormValues>({ name: 'planet' });
  const { field: searchTypeField } = useController({
    control,
    name: 'searchType',
  });
  const planetsQuery = useGetApiV1Planet();
  const zonesQuery = useGetApiV1PlanetPlanetIdZone(String(planet ?? ''), {
    query: {
      queryKey: getGetApiV1PlanetPlanetIdZoneQueryKey(String(planet ?? '')),
      enabled: Boolean(String(planet ?? '').trim()),
    },
  });
  const zones = zonesQuery.data ?? [];

  useEffect((): void => {
    if (String(planet ?? '').trim() || !planetsQuery.data) {
      return;
    }

    const defaultPlanet = planetsQuery.data.find(
      (availablePlanet): boolean => availablePlanet.name === 'Calypso',
    );
    if (defaultPlanet) {
      setValue('planet', defaultPlanet.id, { shouldValidate: true });
    }
  }, [planet, planetsQuery.data, setValue]);

  useEffect((): void => {
    setValue('zone', '');
  }, [planet, setValue]);

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
          <legend id="mining-session-search-type-label">
            {t('MINING.SEARCH_TYPE')}
          </legend>
          <RadioGroup
            name={searchTypeField.name}
            value={searchTypeField.value}
            onValueChange={searchTypeField.onChange}
            onBlur={searchTypeField.onBlur}
            aria-labelledby="mining-session-search-type-label"
            className={styles.options}
          >
            <div className={styles.searchTypeColumn}>
              {[
                ['E', t('MINING.ENMATTER')],
                ['O', t('MINING.ORE')],
              ].map(([value, label]): import('react').JSX.Element => (
                <label key={value} className={styles.option}>
                  <RadioGroupItem value={value} id={`search-type-${value}`} />
                  <span>{label}</span>
                </label>
              ))}
            </div>
            <div className={styles.searchTypeColumn}>
              <label className={styles.option}>
                <RadioGroupItem value="OE" id="search-type-oe" />
                <span>{t('MINING.ORE_ENMATTER')}</span>
              </label>
            </div>
          </RadioGroup>
        </fieldset>
        <SelectRHF
          name="planet"
          label={t('MINING.PLANET')}
          required
          options={[
            { value: '', label: '—' },
            ...(planetsQuery.data ?? []).map(
              (availablePlanet): { value: string; label: string } => ({
                value: availablePlanet.id,
                label: availablePlanet.name,
              }),
            ),
          ]}
        />
        <ComboboxRHF
          name="zone"
          label={t('MINING.ZONE')}
          options={zones.map((zone): { value: string; label: string } => ({
            value: zone.id,
            label: zone.name,
          }))}
          disabled={!String(planet ?? '').trim()}
        />
      </div>
    </Section>
  );
}

export default MiningSessionBaseSection;
