
import "./Spinner.css";
type SpinnerProps = {
  label?: string;
};

export function Spinner({
  label = "Loading",
}: SpinnerProps) {
  return (
    <div
      className="ui-spinner"
      role="status"
      aria-label={label}
    >
      <span
        className="ui-spinner-circle"
        aria-hidden="true"
      />
    </div>
  );
}
