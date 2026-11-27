
import type { SelectHTMLAttributes } from "react";
import "./Select.css";

type SelectOption = {
  value: string;
  label: string;
};

type SelectProps = SelectHTMLAttributes<HTMLSelectElement> & {
  id: string;
  label: string;
  options: SelectOption[];
};

export function Select({
  id,
  label,
  options,
  ...props
}: SelectProps) {
  return (
    <div className="ui-select-field">
      <label htmlFor={id}>{label}</label>

      <select id={id} {...props}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
