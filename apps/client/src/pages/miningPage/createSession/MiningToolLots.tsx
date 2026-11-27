import { useState, type ReactNode } from 'react';
import { useFormContext } from 'react-hook-form';
import { useTranslations } from '@/i18n/useTranslations';
import {
  AppIcon,
  EntropiaImage,
  SelectRHF,
  SubSection,
} from '@/shared/components';
import { getItemImageUrl } from '@/config/images';
import type {
  FinderResponse,
  UnstackableLotResponse,
} from '@/api/generated/model';
import type { MiningSessionFormValues } from '@/shared/types/mining';
import { formatDecimalValue } from '@/shared/utils';
import styles from './mining-session-form.module.scss';

type MiningToolLot = {
  item: Pick<FinderResponse, 'name' | 'imgId'>;
  lot: UnstackableLotResponse;
};

type SelectedToolLot = MiningToolLot & {
  subtitle: string;
  highlight?: boolean;
  details: ReactNode;
};

/** Show the tool image, name, tier, and a subtitle for a picker option or selected card. */
function ToolIdentity({
  item,
  lot,
  subtitle,
  highlight,
}: MiningToolLot & {
  subtitle: string;
  highlight?: boolean;
}): import('react').JSX.Element {
  return (
    <div className={styles.itemRow}>
      <div aria-hidden="true">
        <EntropiaImage url={getItemImageUrl(item.imgId)} alt="" size="small" />
      </div>
      <span>
        {item.name} · T{lot.tier ?? 0}
        <br />{' '}
        <small className={highlight ? styles.enhancedDepth : undefined}>
          {subtitle}
        </small>
      </span>
    </div>
  );
}

/** Select and remove owned tool lots through RHF using caller-provided eligibility and card details. */
export function MiningToolLots({
  field,
  title,
  chooseLabel,
  addLabel,
  options,
  selectedIds,
  selected,
  additionalOptions,
}: {
  field: 'finderLotIds' | 'excavatorLotIds';
  title: string;
  chooseLabel: string;
  addLabel: string;
  options: MiningToolLot[];
  selectedIds: string[];
  selected: SelectedToolLot[];
  additionalOptions: MiningToolLot[];
}): import('react').JSX.Element {
  const { t } = useTranslations();
  const { setValue } = useFormContext<MiningSessionFormValues>();
  const [pickerMode, setPickerMode] = useState<'hidden' | 'add' | 'replace'>(
    'hidden',
  );

  /** Format the lot's current TT for the visible option and keyboard typeahead. */
  const renderOption = ({ item, lot }: MiningToolLot) => {
    const tt = formatDecimalValue(lot.tt);
    return {
      value: lot.id,
      label: `${item.name} · T${lot.tier ?? 0} · ${tt}`,
      content: <ToolIdentity item={item} lot={lot} subtitle={tt} />,
    };
  };

  /** Remove the lot from the form and offer a replacement while other lots remain. */
  const removeTool = (id: string): void => {
    const remainingIds = selectedIds.filter((selectedId) => selectedId !== id);
    setPickerMode(remainingIds.length ? 'replace' : 'hidden');
    setValue(field, remainingIds, { shouldDirty: true, shouldValidate: true });
  };

  /** Restore the add button when the appended-lot picker closes. */
  const handlePickerOpenChange = (open: boolean): void => {
    if (!open) setPickerMode('hidden');
  };

  return (
    <SubSection>
      <h3>{title}</h3>
      <div className={styles.lotList}>
        {!selected.length && options.length > 0 && (
          <SelectRHF
            variant="custom"
            name={field}
            selection="replace"
            label={chooseLabel}
            trigger={chooseLabel}
            options={options.map(renderOption)}
          />
        )}
        {!options.length && (
          <p className={styles.muted}>{t('MINING.SETUP.NO_TOOLS')}</p>
        )}
        {selected.map(({ item, lot, subtitle, highlight, details }) => (
          <div key={lot.id} className={styles.finderCard}>
            <div className={styles.finderCardHeader}>
              <ToolIdentity
                item={item}
                lot={lot}
                subtitle={subtitle}
                highlight={highlight}
              />
              <button
                type="button"
                className={styles.removeEquipment}
                aria-label={t('MINING.SETUP.REMOVE_TOOL').replace(
                  '{tool}',
                  `${item.name} · T${lot.tier ?? 0}`,
                )}
                onClick={() => removeTool(lot.id)}
              >
                <AppIcon name="Trash2" size={16} aria-hidden="true" />
              </button>
            </div>
            <div className={styles.muted}>{details}</div>
          </div>
        ))}
        {selected.length > 0 &&
          additionalOptions.length > 0 &&
          (pickerMode === 'hidden' ? (
            <button
              type="button"
              className={styles.addFinder}
              aria-label={addLabel}
              aria-haspopup="listbox"
              onClick={() => setPickerMode('add')}
            >
              <span aria-hidden="true">+</span>
            </button>
          ) : (
            <SelectRHF
              variant="custom"
              name={field}
              label={addLabel}
              trigger={chooseLabel}
              options={additionalOptions.map(renderOption)}
              selection="append"
              defaultOpen={pickerMode === 'add'}
              onOpenChange={handlePickerOpenChange}
              onSelect={() => setPickerMode('hidden')}
            />
          ))}
      </div>
    </SubSection>
  );
}
