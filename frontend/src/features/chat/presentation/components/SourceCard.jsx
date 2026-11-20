import React from "react";

export default function SourceCard({ source }) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-2 rounded-md border border-gray-200 px-2 py-1 text-xs text-indigo-600 hover:bg-indigo-50 dark:border-gray-700 dark:text-indigo-400 dark:hover:bg-gray-700"
    >
      <svg className="h-3 w-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
      </svg>
      <span className="truncate">{source.title || source.url}</span>
    </a>
  );
}
