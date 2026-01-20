"use client";

interface StreamingTextProps {
  text: string;
  isStreaming: boolean;
  className?: string;
}

export function StreamingText({
  text,
  isStreaming,
  className = "",
}: StreamingTextProps) {
  return (
    <span className={className}>
      {text}
      {isStreaming && (
        <span className="inline-block w-0.5 h-4 bg-foreground ml-0.5 animate-blink align-middle" />
      )}
    </span>
  );
}

// Add this to your global CSS or Tailwind config
// @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
// .animate-blink { animation: blink 1s step-end infinite; }
