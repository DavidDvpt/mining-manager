import { useTranslations } from '@/i18n/useTranslations';
import { setDocumentLocale, type Locale } from '@/i18n/locale';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';
import styles from './toolbar.module.scss';

/** Render the language selector and reload the application after a locale change. */
export function LanguageSelector() {
  const { locale, t } = useTranslations();

  const handleChange = (value: string) => {
    setDocumentLocale(value as Locale);
    window.location.reload();
  };

  return (
    <div className={styles.languageSelector}>
      <span className={styles.visuallyHidden}>{t('APP.LANGUAGE')}</span>
      <Select
        value={locale}
        onValueChange={handleChange}
      >
        <SelectTrigger
          className={styles.languageTrigger}
          aria-label={t('APP.LANGUAGE')}
        >
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="fr_FR">
            <span role="img" aria-label={t('APP.FRENCH_FLAG')}>
              🇫🇷
            </span>&nbsp;
            FR
          </SelectItem>
          <SelectItem value="en_EN">
            <span role="img" aria-label={t('APP.ENGLISH_FLAG')}>
              🇬🇧
            </span>&nbsp;
            EN
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}

export default LanguageSelector;
