import { useTranslations } from '@/i18n/useTranslations';
import { useEffect } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';
import { AppIcon, SelectRHF, SubSection } from '@/shared/components';
import type { MiningSessionFormValues } from '@/shared/types/mining';
import type { MiningEquipment } from './useMiningEquipment';
import styles from './mining-session-form.module.scss';

type Props = {
  equipment: MiningEquipment;
  socketTier: number;
  tool?: 'FINDER' | 'EXCAVATOR';
};

/** Show a shared enhancer list up to the supplied socket tier and clear incompatible selections. */
export function MiningEnhancersBlock({
  equipment,
  socketTier,
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
            item.details.socket <= socketTier,
        )
      )
        setValue(`${field}.${socket}`, '', { shouldValidate: true });
    }
  }, [selected, available, socketTier, field, setValue]);
  return (
    <SubSection>
      <h3>{t('MINING.ENHANCERS')}</h3>
      <p className={styles.muted}>
        {t(
          tool === 'FINDER'
            ? 'MINING.SETUP.COMMON_TIER'
            : 'MINING.SETUP.MAX_TIER',
        )}
        {' : '}
        {socketTier} · {t('MINING.SETUP.DEFERRED_USAGE')}
      </p>
      <div className={styles.socketList}>
        {Array.from({ length: socketTier }, (_, index) => {
          const socket = index + 1;
          const socketKey = `s${socket}` as const;
          const name = `${field}.${socketKey}` as const;
          const label = `${t('MINING.SOCKET')} ${socket}`;
          const options = available
            .filter((item) => item.details.socket === socket)
            .map((item) => ({
              value: item.id,
              label: `${item.name.replace(/^.*?\b(?=Mining\b)/u, '')} · ${equipment.enhancerStock[item.id]}`,
            }));
          const chosen = options.find(
            (option) => option.value === selected[socketKey],
          );
          /** Clear this socket in the form so its picker reappears. */
          const removeEnhancer = (): void => {
            setValue(name, '', { shouldDirty: true, shouldValidate: true });
          };
          return chosen ? (
            <div key={socket} className={styles.socketSelection}>
              <span>{label}</span>
              <span>{chosen.label}</span>
              <button
                type="button"
                className={styles.removeEquipment}
                aria-label={t('MINING.SETUP.REMOVE_ENHANCER').replace(
                  '{socket}',
                  label,
                )}
                onClick={removeEnhancer}
              >
                <AppIcon name="Trash2" size={16} aria-hidden="true" />
              </button>
            </div>
          ) : (
            <SelectRHF
              key={socket}
              inline
              name={name}
              label={label}
              options={[
                { value: '', label: t('MINING.NO_ENHANCER') },
                ...options,
              ]}
            />
          );
        })}
      </div>
      {!socketTier && (
        <p className={styles.muted}>{t('MINING.SETUP.NO_SOCKETS')}</p>
      )}
    </SubSection>
  );
}
export default MiningEnhancersBlock;
