
import "./Modal.css";
import {
  useEffect,
  useId,
  useRef,
  type ReactNode,
} from "react";

type ModalProps = {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
};

export function Modal({
  isOpen,
  onClose,
  title,
  children,
}: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const titleId = useId();

  useEffect(() => {
    const dialog = dialogRef.current;

    if (!dialog) return;

    if (isOpen && !dialog.open) {
      dialog.showModal();
    }

    if (!isOpen && dialog.open) {
      dialog.close();
    }
  }, [isOpen]);

  return (
    <dialog
      ref={dialogRef}
      className="ui-modal"
      aria-labelledby={titleId}
      onCancel={onClose}
    >
      <div className="ui-modal-header">
        <h2 id={titleId}>{title}</h2>

        <button
          type="button"
          onClick={onClose}
          aria-label="Close dialog"
        >
          ×
        </button>
      </div>

      <div className="ui-modal-body">
        {children}
      </div>
    </dialog>
  );
}
