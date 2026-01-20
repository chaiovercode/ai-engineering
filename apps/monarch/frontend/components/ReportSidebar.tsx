"use client";

import type { SavedReport } from "@/lib/storage";
import { ReportHistoryItem } from "./ReportHistoryItem";

interface ReportSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  reports: SavedReport[];
  activeReportId: string | null;
  onSelectReport: (report: SavedReport) => void;
  onDeleteReport: (id: string) => void;
  onUpdateTitle: (id: string, title: string) => void;
}

function ChevronLeftIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M15 18l-6-6 6-6" />
    </svg>
  );
}

function ChevronRightIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 18l6-6-6-6" />
    </svg>
  );
}

function HistoryIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

function FolderIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
    </svg>
  );
}

export function ReportSidebar({
  isOpen,
  onToggle,
  reports,
  activeReportId,
  onSelectReport,
  onDeleteReport,
  onUpdateTitle,
}: ReportSidebarProps) {
  return (
    <aside
      className={`
        flex-shrink-0 flex flex-col h-full
        bg-[var(--paper)]
        border-r-2 border-[var(--ink)]
        transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]
        ${isOpen ? "w-80" : "w-16"}
      `}
    >
      {isOpen ? (
        /* ═══════════════════════════════════════════════════════════
           EXPANDED STATE
           ═══════════════════════════════════════════════════════════ */
        <>
          {/* Header */}
          <div className="flex-shrink-0 flex items-center justify-between px-5 py-4 bg-[var(--ink)] border-b-2 border-[var(--ink)]">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 border-2 border-[var(--gold)] bg-[var(--ink-light)] flex items-center justify-center">
                <HistoryIcon className="w-4 h-4 text-[var(--gold)]" />
              </div>
              <div>
                <h2 className="font-semibold text-[var(--paper)] text-sm tracking-wide">History</h2>
                {reports.length > 0 && (
                  <span className="text-[10px] text-[var(--slate-light)]">
                    {reports.length} report{reports.length !== 1 ? "s" : ""}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={onToggle}
              className="w-8 h-8 flex items-center justify-center border-2 border-[var(--paper)] bg-transparent hover:bg-[var(--paper)] hover:text-[var(--ink)] text-[var(--paper)] transition-colors"
              title="Collapse sidebar (Esc)"
            >
              <ChevronLeftIcon className="w-4 h-4" />
            </button>
          </div>

          {/* Report list */}
          <div className="flex-1 overflow-y-auto">
            {reports.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center p-8 text-center">
                <div className="w-16 h-16 border-2 border-[var(--slate-light)] bg-white flex items-center justify-center mb-4">
                  <FolderIcon className="w-8 h-8 text-[var(--slate)]" />
                </div>
                <p className="text-sm font-medium text-[var(--ink)] mb-1">No saved reports</p>
                <p className="text-xs text-[var(--slate)] max-w-[180px]">
                  Generated reports will automatically appear here
                </p>
              </div>
            ) : (
              <div className="py-2">
                {reports.map((report) => (
                  <ReportHistoryItem
                    key={report.id}
                    report={report}
                    isActive={report.id === activeReportId}
                    onClick={() => onSelectReport(report)}
                    onDelete={() => onDeleteReport(report.id)}
                    onUpdateTitle={(title) => onUpdateTitle(report.id, title)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex-shrink-0 px-4 py-3 border-t-2 border-[var(--ink)] bg-white">
            <p className="text-[10px] text-[var(--slate)] text-center">
              Press <kbd className="px-1.5 py-0.5 bg-[var(--paper)] border border-[var(--ink)] text-[9px] font-mono">Esc</kbd> to toggle
            </p>
          </div>
        </>
      ) : (
        /* ═══════════════════════════════════════════════════════════
           COLLAPSED STATE
           ═══════════════════════════════════════════════════════════ */
        <div className="h-full flex flex-col items-center bg-[var(--ink)]">
          {/* Expand button */}
          <div className="flex-shrink-0 py-4">
            <button
              onClick={onToggle}
              className="w-10 h-10 flex items-center justify-center border-2 border-[var(--paper)] bg-transparent hover:bg-[var(--paper)] hover:text-[var(--ink)] text-[var(--paper)] transition-all"
              title="Expand sidebar"
            >
              <ChevronRightIcon className="w-5 h-5" />
            </button>
          </div>

        </div>
      )}
    </aside>
  );
}
