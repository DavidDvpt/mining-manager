import { useTranslations } from '@/i18n/useTranslations';
import { useEffect } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';
import { SelectRHF, SubSection, EntropiaImage } from '@/shared/components';
import { getItemImageUrl } from '@/config/images';
import type { MiningSessionFormValues } from '@/shared/types/mining';
import type { MiningEquipment } from './useMiningEquipment';
import styles from './mining-session-form.module.scss';

type Props = {
  equipment: MiningEquipment;
  minimumFinderTier: number;
  tool?: 'FINDER' | 'EXCAVATOR';
};

/** Render stock per socket up to the lowest selected tier and clear incompatible enhancers. */
export function MiningEnhancersBlock({
  equipment,
  minimumFinderTier,
  tool = 'FINDER',
}: Props): import('react').JSX.Element {
  const { t } = useTranslations();
  const { control, setValue } = useFormContext<MiningSessionFormValues>();
  const field = tool === 'FINDER' ? 'enhancers' : 'excavatorEnhancers';
  const selected = useWatch({ control, name: field });
  const available = equipment.enhancers.filter(
    (item) =>
      item.details.tool === tool && (equipment.enhancerStock[item.id] ?? 0) > 0,
  );
  useEffect(() => {
    for (const [socket, id] of Object.entries(selected)) {
      if (
        id &&
        !available.some(
          (item) =>
            item.id === id &&
            socket === `s${item.details.socket}` &&
            item.details.socket <= minimumFinderTier,
        )
      )
        setValue(`${field}.${socket}`, '', { shouldValidate: true });
    }
  }, [selected, available, minimumFinderTier, field, setValue]);
  return (
    <SubSection>
      <h3>{t('MINING.ENHANCERS')}</h3>
      <p className={styles.muted}>
        {t('MINING.SETUP.COMMON_TIER')} : {minimumFinderTier} ·{' '}
        {t('MINING.SETUP.DEFERRED_USAGE')}
      </p>
      <div className={styles.socketList}>
        {Array.from({ length: minimumFinderTier }, (_, index) => {
          const socket = index + 1;
          const items = available.filter(
            (item) => item.details.socket === socket,
          );
          const selectedItem = items.find(
            (item) => item.id === selected[`s${socket}`],
          );
          return (
            <div key={socket}>
              <SelectRHF
                name={`${field}.s${socket}`}
                label={`${t('MINING.SOCKET')} ${socket}`}
                options={[
                  { value: '', label: t('MINING.NO_ENHANCER') },
                  ...items.map((item) => ({
                    value: item.id,
                    label: `${item.name} · ${equipment.enhancerStock[item.id]} ${t('MINING.SETUP.AVAILABLE')}`,
                  })),
                ]}
              />
              {selectedItem && (
                <div className={styles.itemRow}>
                  <EntropiaImage
                    url={getItemImageUrl(selectedItem.imgId)}
                    alt={selectedItem.name}
                    size="small"
                  />
                  <span>
                    {selectedItem.name}
                    <br />
                    <small>
                      {selectedItem.economy.tt ?? '—'}{' '}
                      {t('MINING.SETUP.UNIT_COST')}
                    </small>
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
      {!minimumFinderTier && (
        <p className={styles.muted}>{t('MINING.SETUP.NO_SOCKETS')}</p>
      )}
    </SubSection>
  );
}
export default MiningEnhancersBlock;
