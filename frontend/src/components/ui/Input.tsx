
import type { InputHTMLAttributes } from "react";
import "./Input.css";

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  id: string;
  label: string;
};

export function Input({ id, label, ...props }: InputProps) {
  return (
    <div className="ui-input-field">
      <label htmlFor={id}>{label}</label>
      <input id={id} {...props} />
    </div>
  );
}
