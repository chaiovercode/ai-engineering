"use client";

import { useEffect, useCallback } from "react";

export interface KeyboardShortcuts {
  onGenerate?: () => void;
  onGenerateB?: () => void;
  onSwitchToA?: () => void;
  onSwitchToB?: () => void;
  onSave?: () => void;
  onToggleSidebar?: () => void;
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcuts): void {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const isMod = event.metaKey || event.ctrlKey;

      // Ignore if typing in an input/textarea
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement
      ) {
        // Allow Cmd+Enter in textarea
        if (isMod && event.key === "Enter") {
          event.preventDefault();
          shortcuts.onGenerate?.();
        }
        return;
      }

      // Cmd/Ctrl + Enter: Generate
      if (isMod && event.key === "Enter") {
        event.preventDefault();
        shortcuts.onGenerate?.();
        return;
      }

      // Cmd/Ctrl + B: Generate Version B
      if (isMod && event.key === "b") {
        event.preventDefault();
        shortcuts.onGenerateB?.();
        return;
      }

      // Cmd/Ctrl + 1: Switch to Version A
      if (isMod && event.key === "1") {
        event.preventDefault();
        shortcuts.onSwitchToA?.();
        return;
      }

      // Cmd/Ctrl + 2: Switch to Version B
      if (isMod && event.key === "2") {
        event.preventDefault();
        shortcuts.onSwitchToB?.();
        return;
      }

      // Cmd/Ctrl + S: Manual save
      if (isMod && event.key === "s") {
        event.preventDefault();
        shortcuts.onSave?.();
        return;
      }

      // Escape: Toggle/close sidebar
      if (event.key === "Escape") {
        event.preventDefault();
        shortcuts.onToggleSidebar?.();
        return;
      }
    },
    [shortcuts]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);
}

export const KEYBOARD_HINTS = [
  { keys: ["Cmd", "Enter"], action: "Generate" },
  { keys: ["Cmd", "B"], action: "Version B" },
  { keys: ["Cmd", "1/2"], action: "Switch versions" },
  { keys: ["Cmd", "S"], action: "Save" },
  { keys: ["Esc"], action: "Toggle sidebar" },
];
