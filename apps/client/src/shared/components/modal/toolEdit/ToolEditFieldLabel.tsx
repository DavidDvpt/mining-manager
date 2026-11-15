import type { ReactNode } from 'react';
import styles from './tool-edit-modal.module.scss';

type ToolEditFieldLabelProps = {
  children: ReactNode;
  range: string;
};

/** Render a compact tool-edit label with a muted input range hint. */
export function ToolEditFieldLabel({
  children,
  range,
}: ToolEditFieldLabelProps) {
  return (
    <>
      {children}&nbsp;
      <span className={styles.mutedHint}>({range})</span>
    </>
  );
}

export default ToolEditFieldLabel;
