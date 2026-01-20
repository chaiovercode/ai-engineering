"use client";

export type Tone = "professional" | "conversational" | "punchy";

interface ToneSelectorProps {
  value: Tone;
  onChange: (tone: Tone) => void;
  disabled?: boolean;
}

const tones: { value: Tone; label: string }[] = [
  { value: "professional", label: "Formal" },
  { value: "conversational", label: "Casual" },
  { value: "punchy", label: "Punchy" },
];

export function ToneSelector({ value, onChange, disabled }: ToneSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-xs font-bold uppercase tracking-wide text-[var(--slate)]">
        Tone
      </label>
      <div className="grid grid-cols-3 gap-2">
        {tones.map((tone) => (
          <button
            key={tone.value}
            onClick={() => onChange(tone.value)}
            disabled={disabled}
            className={`
              px-2 py-1.5 text-xs font-semibold text-center border-2 transition-all
              ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
              ${
                value === tone.value
                  ? "border-[var(--ink)] bg-[var(--ink)] text-[var(--paper)] shadow-[2px_2px_0px_var(--gold)]"
                  : "border-[var(--slate-light)] bg-white text-[var(--ink)] hover:border-[var(--ink)] hover:shadow-[2px_2px_0px_var(--ink)]"
              }
            `}
          >
            {tone.label}
          </button>
        ))}
      </div>
    </div>
  );
}
