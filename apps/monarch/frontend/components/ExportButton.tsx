"use client";

import { useState, useRef } from "react";
import { exportToPng, copyToClipboard } from "@/lib/export";

interface ExportButtonProps {
  targetRef: React.RefObject<HTMLElement | null>;
  filename: string;
  className?: string;
}

function DownloadIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );
}

function ClipboardIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="9" y="9" width="13" height="13" rx="0" />
      <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
    </svg>
  );
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}


export function ExportButton({ targetRef, filename, className = "" }: ExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [copied, setCopied] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleDownload = async () => {
    if (!targetRef.current) return;
    setIsExporting(true);
    try {
      await exportToPng(targetRef.current, `${filename}.png`);
    } catch (error) {
      console.error("Export failed:", error);
    } finally {
      setIsExporting(false);
      setIsOpen(false);
    }
  };

  const handleCopy = async () => {
    if (!targetRef.current) return;
    setIsExporting(true);
    try {
      await copyToClipboard(targetRef.current);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Copy failed:", error);
    } finally {
      setIsExporting(false);
      setIsOpen(false);
    }
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isExporting}
        className="brutal-button p-1.5 bg-white disabled:opacity-50"
        title={copied ? "Copied!" : "Export image"}
      >
        {isExporting ? (
          <span className="w-4 h-4 border-2 border-[var(--ink)] border-t-transparent rounded-full animate-spin" />
        ) : copied ? (
          <CheckIcon className="w-4 h-4 text-[var(--gold)]" />
        ) : (
          <DownloadIcon className="w-4 h-4" />
        )}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 top-full mt-1 z-20 bg-white border-2 border-[var(--ink)] shadow-[3px_3px_0px_var(--ink)] min-w-[140px]">
            <button
              onClick={handleDownload}
              className="w-full flex items-center gap-2 px-3 py-2 text-xs text-left hover:bg-[var(--paper)] transition-colors"
            >
              <DownloadIcon className="w-4 h-4" />
              <span>Download PNG</span>
            </button>
            <button
              onClick={handleCopy}
              className="w-full flex items-center gap-2 px-3 py-2 text-xs text-left hover:bg-[var(--paper)] transition-colors border-t border-[var(--slate-light)]"
            >
              <ClipboardIcon className="w-4 h-4" />
              <span>Copy to clipboard</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
}
