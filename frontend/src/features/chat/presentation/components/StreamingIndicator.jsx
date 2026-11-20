import React from "react";

export default function StreamingIndicator({ content }) {
  return (
    <div className="flex w-full justify-start">
      <div className="max-w-[80%] rounded-xl bg-gray-100 px-4 py-3 dark:bg-gray-800">
        {content ? (
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-gray-900 dark:text-gray-100">
            {content}
            <span className="ml-1 inline-block animate-pulse">|</span>
          </p>
        ) : (
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500 [animation-delay:0ms]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500 [animation-delay:150ms]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500 [animation-delay:300ms]" />
            </div>
            <span className="text-xs text-gray-500">Researching...</span>
          </div>
        )}
      </div>
    </div>
  );
}
