import { useFormContext } from 'react-hook-form';

import { SelectRHF, SubSection } from '@/shared/components';
import { useTranslations } from '@/i18n/useTranslations';
import type { EnhancerResponse } from '@/api/generated/model/enhancerResponse';

import type { MiningSessionFormValues } from '@/shared/types/mining';
import styles from './mining-session-form.module.scss';

type MiningEnhancersBlockProps = {
  minimumFinderTier: number;
  enhancers: EnhancerResponse[];
  stock: Record<string, number>;
};

/** Render one RHF enhancer select for every socket allowed by the finder tier. */
export function MiningEnhancersBlock({
  minimumFinderTier,
  enhancers,
  stock,
}: MiningEnhancersBlockProps): import('react').JSX.Element {
  const { t } = useTranslations();
  useFormContext<MiningSessionFormValues>();

  return (
    <SubSection>
      <h3>{t('MINING.ENHANCERS')}</h3>
      {minimumFinderTier > 0 ? (
        <div className={styles.socketList}>
          {Array.from(
            { length: minimumFinderTier },
            (_, index): import('react').JSX.Element => {
              const socket = index + 1;
              const options = enhancers
                .filter(
                  (enhancer): boolean => enhancer.details.socket === socket,
                )
                .map((enhancer): { value: string; label: string } => ({
                  value: enhancer.id,
                  label: `${enhancer.name} / ${stock[enhancer.id] ?? 0}`,
                }));

              return (
                <SelectRHF
                  key={socket}
                  name={`enhancers.${socket}`}
                  label={`${t('MINING.SOCKET')} ${socket}`}
                  options={[
                    { value: '', label: t('MINING.NO_ENHANCER') },
                    ...options,
                  ]}
                />
              );
            },
          )}
        </div>
      ) : (
        <p className={styles.muted}>{t('MINING.NO_ENHANCERS')}</p>
      )}
    </SubSection>
  );
}

export default MiningEnhancersBlock;
