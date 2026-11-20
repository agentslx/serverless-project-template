import React from "react";

export function MdButton({
  variant = "filled",
  size = "md",
  children,
  className = "",
  ...rest
}) {
  const base =
    "inline-flex items-center justify-center font-medium rounded-full " +
    "transition-[background,box-shadow,transform] active:scale-[0.98] " +
    "disabled:opacity-50 disabled:pointer-events-none focus-visible:outline-none " +
    "focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 " +
    "focus-visible:ring-offset-surface tracking-[0.01em]";
  const sizes = {
    sm: "h-9 px-4 text-sm",
    md: "h-10 px-6 text-sm",
    lg: "h-12 px-7 text-base",
  };
  const variants = {
    filled: "bg-primary text-on-primary hover:shadow-md3-2 hover:bg-primary/95",
    tonal: "bg-secondary-container text-on-secondary-container hover:shadow-md3-1 hover:brightness-95",
    outlined: "border border-outline text-primary hover:bg-primary/[0.08]",
    text: "text-primary hover:bg-primary/[0.08] px-3",
  };
  return (
    <button
      {...rest}
      className={`${base} ${sizes[size]} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
}
