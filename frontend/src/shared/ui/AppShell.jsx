import React from "react";
import { Link, useLocation } from "react-router-dom";
import { adminAppUrl } from "@/aws-config";

/** Material 3 inspired top-app-bar + page surface — USER app. */
export function AppShell({ children, currentUser }) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header
        data-testid="top-app-bar"
        className="h-16 flex items-center px-6 sticky top-0 z-10 bg-surface/80 backdrop-blur border-b border-outline-variant"
      >
        <Link
          to="/"
          data-testid="brand-link"
          className="flex items-center gap-2 text-on-surface no-underline"
        >
          <span className="material-symbols-rounded text-primary">rocket_launch</span>
          <span className="font-semibold tracking-tight">Template</span>
        </Link>
        <div className="flex-1" />
        {currentUser && (
          <span
            data-testid="current-user-email"
            className="text-sm text-on-surface-variant mr-3"
          >
            {currentUser.email}
          </span>
        )}
        <a
          href={adminAppUrl}
          target="_blank"
          rel="noreferrer"
          data-testid="admin-app-link"
          className="text-sm text-primary hover:underline"
        >
          Admin app ↗
        </a>
      </header>
      <main className="flex-1 px-6 py-10 max-w-5xl mx-auto w-full">{children}</main>
      <footer className="px-6 py-4 text-xs text-on-surface-variant text-center">
        emergent-serverless-template · user app · {process.env.REACT_APP_FLAVOR || "dev"} ·{" "}
        {process.env.REACT_APP_AWS_REGION || "ap-southeast-2"}
      </footer>
    </div>
  );
}
