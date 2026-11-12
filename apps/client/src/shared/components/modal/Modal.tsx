import type { PropsWithChildren, ReactNode } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { cn } from '@/lib/utils/styles';
import styles from './modal.module.scss';

export type ModalProps = PropsWithChildren<{
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title?: ReactNode;
  description?: ReactNode;
  noClose?: boolean;
  className?: string;
}>;

/** Provide the shared controlled modal shell used by forms and confirmations. */
export function Modal({
  open,
  onOpenChange,
  title,
  description,
  noClose = false,
  className,
  children,
}: ModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className={cn(styles.content, className)}
        onInteractOutside={(event) => {
          if (noClose) event.preventDefault();
        }}
        onEscapeKeyDown={(event) => {
          if (noClose) event.preventDefault();
        }}
      >
        {title || description ? (
          <DialogHeader>
            {title ? <DialogTitle>{title}</DialogTitle> : null}
            {description ? (
              <DialogDescription>{description}</DialogDescription>
            ) : null}
          </DialogHeader>
        ) : null}

        {children}
      </DialogContent>
    </Dialog>
  );
}

export default Modal;
