import { useTranslations } from '@/i18n/useTranslations';
import { CheckboxRHF, EntropiaImage, SubSection } from '@/shared/components';
import { getItemImageUrl } from '@/config/images';
import type { MiningEquipment } from './useMiningEquipment';
import styles from './mining-session-form.module.scss';

/** List available excavator lots and bind each checkbox to the selected excavators. */
export function MiningExcavatorsBlock({
  equipment,
}: {
  equipment: MiningEquipment;
}): import('react').JSX.Element {
  const { t } = useTranslations();
  const options = equipment.lots
    .slice()
    .sort(
      (a, b) =>
        Number(a.tt ?? 0) - Number(b.tt ?? 0) || a.id.localeCompare(b.id),
    )
    .flatMap((lot) => {
      const item = equipment.excavators.find((tool) => tool.id === lot.item.id);
      return item ? [{ item, lot }] : [];
    });
  return (
    <SubSection>
      <h3>{t('MINING.SETUP.EXCAVATORS')}</h3>
      <div className={styles.lotList}>
        {options.map(({ item, lot }) => (
          <div key={lot.id} className={styles.itemRow}>
            <EntropiaImage
              url={getItemImageUrl(item.imgId)}
              alt={item.name}
              size="small"
            />
            <div>
              <CheckboxRHF
                name="excavatorLotIds"
                checkedValue={lot.id}
                label={`${item.name} · T${lot.tier ?? 0}`}
              />
              <small>
                {item.details.isLimited
                  ? `${lot.tt ?? '—'} TT · L`
                  : t('MINING.SETUP.REPAIRABLE')}
              </small>
              <p className={styles.muted}>{t('MINING.SETUP.CLOSING_COST')}</p>
            </div>
          </div>
        ))}
      </div>
      {!options.length && (
        <p className={styles.muted}>{t('MINING.SETUP.NO_TOOLS')}</p>
      )}
    </SubSection>
  );
}
