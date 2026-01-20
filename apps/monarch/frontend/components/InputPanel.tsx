"use client";

import { ToneSelector, type Tone } from "./ToneSelector";

interface InputPanelProps {
  value: string;
  onChange: (value: string) => void;
  onGenerate: () => void;
  isLoading: boolean;
  tone: Tone;
  onToneChange: (tone: Tone) => void;
}

function ArrowIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>
  );
}

function LoadingSpinner({ className }: { className?: string }) {
  return (
    <svg className={`animate-spin ${className}`} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeOpacity="0.25" />
      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

export function InputPanel({
  value,
  onChange,
  onGenerate,
  isLoading,
  tone,
  onToneChange,
}: InputPanelProps) {
  return (
    <div className="bg-white border-2 border-[var(--ink)] shadow-[4px_4px_0px_var(--ink)] h-full flex flex-col">
      <div className="px-5 py-4 border-b-2 border-[var(--ink)] bg-[var(--ink)]">
        <h3 className="text-sm font-bold uppercase tracking-wide text-[var(--paper)]">Paste Report</h3>
      </div>
      <div className="flex-1 flex flex-col p-5 gap-4">
        <textarea
          placeholder="Paste your IC research report here..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 min-h-[280px] resize-none px-4 py-3 text-sm leading-relaxed bg-white border-2 border-[var(--slate-light)] focus:border-[var(--gold)] focus:ring-1 focus:ring-[var(--gold)] outline-none transition-colors"
        />

        <ToneSelector
          value={tone}
          onChange={onToneChange}
          disabled={isLoading}
        />

        <button
          onClick={onGenerate}
          disabled={isLoading || !value.trim()}
          className="brutal-button-gold w-full py-3 px-6 uppercase tracking-wide flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <LoadingSpinner className="w-4 h-4" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <span>Generate</span>
              <ArrowIcon className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
