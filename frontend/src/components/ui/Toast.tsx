
import "./Toast.css";

type ToastProps = {
  message: string;
  variant?: "success" | "error" | "info";
  onClose: () => void;
};

export function Toast({
  message,
  variant = "info",
  onClose,
}: ToastProps) {
  return (
    <div
      className={`ui-toast ui-toast--${variant}`}
      role={variant === "error" ? "alert" : "status"}
    >
      <span>{message}</span>

      <button
        type="button"
        onClick={onClose}
        aria-label="Dismiss notification"
      >
        ×
      </button>
    </div>
  );
}
