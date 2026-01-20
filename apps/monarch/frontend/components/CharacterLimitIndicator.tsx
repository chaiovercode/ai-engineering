"use client";

interface CharacterLimitIndicatorProps {
  current: number;
  limit: number;
  className?: string;
}

export function CharacterLimitIndicator({
  current,
  limit,
  className = "",
}: CharacterLimitIndicatorProps) {
  const percentage = Math.min((current / limit) * 100, 100);
  const overLimit = current > limit;
  const overAmount = current - limit;

  // Color logic: gold < 80%, amber 80-100%, red > 100%
  const getBarColor = () => {
    if (overLimit) return "bg-red-500";
    if (percentage >= 80) return "bg-amber-500";
    return "bg-[var(--gold)]";
  };

  const getTextColor = () => {
    if (overLimit) return "text-red-600";
    if (percentage >= 80) return "text-amber-600";
    return "text-[var(--slate)]";
  };

  return (
    <div className={`space-y-1.5 ${className}`}>
      {/* Progress bar */}
      <div className="h-1.5 bg-[var(--paper-dark)] border border-[var(--slate-light)] overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${getBarColor()}`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Counter */}
      <div className="flex items-center justify-between text-xs">
        <span className={`font-mono ${getTextColor()}`}>
          {current.toLocaleString()} / {limit.toLocaleString()}
        </span>
        {overLimit && (
          <span className="text-red-600 font-medium animate-pulse">
            {overAmount.toLocaleString()} over limit
          </span>
        )}
        {!overLimit && percentage >= 80 && (
          <span className="text-amber-600 font-medium">
            {(limit - current).toLocaleString()} remaining
          </span>
        )}
      </div>
    </div>
  );
}

// Platform-specific limits
export const CHARACTER_LIMITS = {
  linkedin: 3000,
  whatsapp: 1000,
} as const;
