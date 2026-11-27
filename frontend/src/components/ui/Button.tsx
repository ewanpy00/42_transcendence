
import type { ReactNode } from "react";
import "./Button.css";

type ButtonProps = {
  children: ReactNode;
  disabled?: boolean;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  variant?: "primary" | "secondary" | "danger";
};

export function Button({
  children,
  disabled = false,
  onClick,
  type = "button",
  variant = "primary",
}: ButtonProps) {
  return (
    <button
      className={`ui-button ui-button--${variant}`}
      type={type}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
