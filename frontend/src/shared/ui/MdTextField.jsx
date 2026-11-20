import React, { useId } from "react";

/** Material-3 outlined text field. */
export function MdTextField({
  label,
  type = "text",
  error,
  helperText,
  testid,
  ...rest
}) {
  const id = useId();
  const helpId = `${id}-help`;
  return (
    <div className="relative w-full">
      <input
        id={id}
        type={type}
        data-testid={testid}
        aria-describedby={helperText || error ? helpId : undefined}
        aria-invalid={!!error}
        placeholder=" "
        className={[
          "peer w-full h-14 rounded-lg bg-surface px-4 pt-5 pb-1 text-on-surface",
          "border outline-none transition-colors",
          error
            ? "border-error focus:border-error"
            : "border-outline focus:border-primary",
        ].join(" ")}
        {...rest}
      />
      <label
        htmlFor={id}
        className={[
          "pointer-events-none absolute left-4 origin-left transition-all",
          "top-4 text-on-surface-variant",
          "peer-focus:top-1.5 peer-focus:text-xs peer-focus:text-primary",
          "peer-[:not(:placeholder-shown)]:top-1.5 peer-[:not(:placeholder-shown)]:text-xs",
          error ? "text-error peer-focus:text-error" : "",
        ].join(" ")}
      >
        {label}
      </label>
      {(helperText || error) && (
        <p
          id={helpId}
          className={`mt-1.5 text-xs ${error ? "text-error" : "text-on-surface-variant"}`}
        >
          {error || helperText}
        </p>
      )}
    </div>
  );
}
