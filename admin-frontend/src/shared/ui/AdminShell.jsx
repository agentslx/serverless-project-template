import React from "react";
import { Link, NavLink } from "react-router-dom";
import { userAppUrl } from "@/aws-config";

const nav = [
  { to: "/admin", label: "Overview", icon: "monitoring", end: true },
  { to: "/admin/users", label: "Users", icon: "groups" },
];

export function AdminShell({ children, currentUser, onLogout }) {
  return (
    <div className="min-h-screen flex bg-background">
      <aside
        data-testid="admin-sidenav"
        className="w-60 shrink-0 bg-surface border-r border-outline-variant flex flex-col"
      >
        <Link
          to="/admin"
          className="h-16 px-5 flex items-center gap-2 border-b border-outline-variant text-on-surface no-underline"
        >
          <span className="material-symbols-rounded text-primary">admin_panel_settings</span>
          <span className="font-semibold tracking-tight">Admin</span>
        </Link>
        <nav className="p-3 flex-1 flex flex-col gap-1">
          {nav.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              data-testid={`nav-${n.label.toLowerCase()}`}
              className={({ isActive }) =>
                [
                  "flex items-center gap-3 h-11 px-4 rounded-full text-sm transition-colors",
                  isActive
                    ? "bg-secondary-container text-on-secondary-container"
                    : "text-on-surface hover:bg-surface-variant",
                ].join(" ")
              }
            >
              <span className="material-symbols-rounded text-[20px]">{n.icon}</span>
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-outline-variant text-xs text-on-surface-variant">
          <a
            href={userAppUrl}
            target="_blank"
            rel="noreferrer"
            data-testid="user-app-link"
            className="block py-2 px-2 hover:underline text-primary"
          >
            User app ↗
          </a>
          <p className="px-2 leading-relaxed">
            admin · {process.env.REACT_APP_FLAVOR || "dev"} ·{" "}
            {process.env.REACT_APP_AWS_REGION || "ap-southeast-2"}
          </p>
        </div>
      </aside>
      <div className="flex-1 flex flex-col">
        <header className="h-16 px-6 flex items-center bg-surface/80 backdrop-blur border-b border-outline-variant sticky top-0 z-10">
          <div className="flex-1" />
          {currentUser && (
            <span
              data-testid="admin-current-email"
              className="text-sm text-on-surface-variant mr-3"
            >
              {currentUser.email}
            </span>
          )}
          {currentUser && (
            <button
              onClick={onLogout}
              data-testid="admin-logout-btn"
              className="text-sm text-primary hover:underline"
            >
              Sign out
            </button>
          )}
        </header>
        <main className="flex-1 px-8 py-10 max-w-6xl w-full">{children}</main>
      </div>
    </div>
  );
}
