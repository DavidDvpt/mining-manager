import { useTranslations } from '@/i18n/useTranslations';
import { formatDecimalValue } from '@/shared/utils';
import { MiningToolLots } from './MiningToolLots';
import type { MiningEquipment } from './useMiningEquipment';

/** Select any owned excavator lots, across models, with decay recorded at session close. */
export function MiningExcavatorsBlock({
  equipment,
  selectedIds,
}: {
  equipment: MiningEquipment;
  selectedIds: string[];
}): import('react').JSX.Element {
  const { t } = useTranslations();
  const options = equipment.lots.flatMap((lot) => {
    const item = equipment.excavators.find((tool) => tool.id === lot.item.id);
    return item ? [{ item, lot }] : [];
  });
  const selected = selectedIds.flatMap((id) => {
    const option = options.find(({ lot }) => lot.id === id);
    if (!option) return [];
    return [
      {
        ...option,
        subtitle: option.item.details.isLimited
          ? `${formatDecimalValue(option.lot.tt)} TT · L`
          : t('MINING.SETUP.REPAIRABLE'),
        details: t('MINING.SETUP.CLOSING_COST'),
      },
    ];
  });

  return (
    <MiningToolLots
      field="excavatorLotIds"
      title={t('MINING.SETUP.EXCAVATORS')}
      chooseLabel={t('MINING.SETUP.CHOOSE_EXCAVATOR')}
      addLabel={t('MINING.SETUP.ADD_EXCAVATOR')}
      options={options}
      selectedIds={selectedIds}
      selected={selected}
      additionalOptions={options.filter(
        ({ lot }) => !selectedIds.includes(lot.id),
      )}
    />
  );
}
