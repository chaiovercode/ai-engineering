"use client";

import { useState } from "react";
import { KEYBOARD_HINTS } from "@/hooks/useKeyboardShortcuts";

function KeyboardIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M7 16h10" />
    </svg>
  );
}

export function KeyboardHints() {
  const [isExpanded, setIsExpanded] = useState(false);
  const isMac = typeof window !== "undefined" && navigator.platform.includes("Mac");
  const modKey = isMac ? "Cmd" : "Ctrl";

  return (
    <div className="fixed bottom-4 right-4 z-30">
      {isExpanded ? (
        <div className="bg-white border-2 border-[var(--ink)] shadow-[4px_4px_0px_var(--ink)] p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-[var(--ink)] uppercase tracking-wide">
              Shortcuts
            </span>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-[var(--slate)] hover:text-[var(--ink)]"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="space-y-1.5">
            {KEYBOARD_HINTS.map(({ keys, action }) => (
              <div key={action} className="flex items-center justify-between gap-4 text-xs">
                <span className="text-[var(--slate)]">{action}</span>
                <div className="flex items-center gap-1">
                  {keys.map((key, i) => (
                    <span key={i}>
                      <kbd className="px-1.5 py-0.5 bg-[var(--paper)] border border-[var(--ink)] text-[10px] font-mono">
                        {key === "Cmd" ? modKey : key}
                      </kbd>
                      {i < keys.length - 1 && <span className="text-[var(--slate)] mx-0.5">+</span>}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <button
          onClick={() => setIsExpanded(true)}
          className="p-2 bg-white border-2 border-[var(--ink)] shadow-[2px_2px_0px_var(--ink)] hover:bg-[var(--paper)] transition-colors"
          title="Keyboard shortcuts"
        >
          <KeyboardIcon className="w-4 h-4 text-[var(--ink)]" />
        </button>
      )}
    </div>
  );
}
