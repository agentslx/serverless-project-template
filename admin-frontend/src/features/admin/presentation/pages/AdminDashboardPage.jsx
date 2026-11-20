import React from "react";
import { useAuth } from "@/features/auth/presentation/state/AuthContext";

const cards = [
  { icon: "groups", label: "Users", value: "–", testid: "metric-users" },
  { icon: "monitoring", label: "Active sessions", value: "–", testid: "metric-sessions" },
  { icon: "warning", label: "Errors (24h)", value: "–", testid: "metric-errors" },
  { icon: "savings", label: "Spend (mo)", value: "–", testid: "metric-spend" },
];

export default function AdminDashboardPage() {
  const { user } = useAuth();
  return (
    <div data-testid="admin-dashboard" className="flex flex-col gap-8">
      <header>
        <h1 className="text-3xl font-medium tracking-tight text-on-surface">Overview</h1>
        <p className="text-sm text-on-surface-variant mt-1">
          Signed in as <span className="font-mono">{user?.email}</span> · admin Cognito pool
        </p>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((c) => (
          <article
            key={c.label}
            data-testid={c.testid}
            className="bg-surface rounded-3xl shadow-md3-1 p-6 border border-outline-variant"
          >
            <span className="material-symbols-rounded text-primary text-[28px]">
              {c.icon}
            </span>
            <p className="mt-4 text-sm text-on-surface-variant">{c.label}</p>
            <p className="mt-1 text-2xl font-medium text-on-surface">{c.value}</p>
          </article>
        ))}
      </section>

      <section
        data-testid="admin-placeholder"
        className="bg-surface rounded-3xl shadow-md3-1 p-8 border border-outline-variant"
      >
        <h2 className="text-base font-medium text-on-surface">Connect AppSync admin queries</h2>
        <p className="mt-2 text-sm text-on-surface-variant leading-relaxed">
          These KPIs become live once you add a `listUsers` admin Lambda + AppSync
          resolver gated by the admin Cognito group. See{" "}
          <code className="font-mono text-primary">system-design-doc/features/admin/</code>.
        </p>
      </section>
    </div>
  );
}
