import React from "react";

export function AuthCard({ title, subtitle, children, footer, testid }) {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-background">
      <section
        data-testid={testid}
        className="w-full max-w-md bg-surface rounded-3xl shadow-md3-2 p-8 border border-outline-variant"
      >
        <div className="flex items-center gap-2 mb-2">
          <span className="material-symbols-rounded text-primary">admin_panel_settings</span>
          <span className="text-xs uppercase tracking-[0.16em] text-on-surface-variant font-semibold">
            Admin Panel
          </span>
        </div>
        <h1 className="text-2xl font-medium tracking-tight text-on-surface">{title}</h1>
        {subtitle && (
          <p className="mt-2 text-sm text-on-surface-variant">{subtitle}</p>
        )}
        <div className="mt-8 flex flex-col gap-5">{children}</div>
        {footer && (
          <div className="mt-8 pt-5 border-t border-outline-variant text-sm text-on-surface-variant">
            {footer}
          </div>
        )}
      </section>
    </div>
  );
}
