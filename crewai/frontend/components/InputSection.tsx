'use client';

import { useState, useEffect } from 'react';
import { colors } from '@/lib/colors';

const examples = [
  'zensar technologies',
  'claude cowork',
  'agentic ai in 2026',
];

interface InputSectionProps {
  onSubmit: (input: string, type: 'topic' | 'url', mode: 'gen-z' | 'analytical') => void;
}

export default function InputSection({ onSubmit }: InputSectionProps) {
  const [input, setInput] = useState('');
  const [currentExample, setCurrentExample] = useState(0);
  const [mode, setMode] = useState<'gen-z' | 'analytical'>('analytical');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentExample((prev) => (prev + 1) % examples.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const detectType = (text: string): 'topic' | 'url' => {
    return text.startsWith('http://') || text.startsWith('https://')
      ? 'url'
      : 'topic';
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSubmit(input.trim(), detectType(input.trim()), mode);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: 'calc(100vh - 80px)',
        padding: '40px 20px',
        opacity: mounted ? 1 : 0.9,
        transition: 'opacity 800ms ease-out',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '480px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
        }}
      >
        {/* Spacer for breathing room */}
        <div style={{ height: '40px' }} />

        {/* Hero text - extremely minimal */}
        <h1
          style={{
            fontSize: '32px',
            fontWeight: 300,
            marginBottom: '24px',
            color: colors.text,
            letterSpacing: '0px',
            lineHeight: '1.2',
            opacity: mounted ? 1 : 0.6,
            transform: mounted ? 'translateY(0)' : 'translateY(10px)',
            transition: 'all 800ms ease-out 100ms',
          }}
        >
          zensar research
        </h1>

        {/* Subtle description */}
        <p
          style={{
            fontSize: '12px',
            color: colors.textLight,
            fontWeight: 300,
            marginBottom: '64px',
            lineHeight: '1.6',
            opacity: mounted ? 0.7 : 0.3,
            transition: 'opacity 800ms ease-out 200ms',
            maxWidth: '280px',
          }}
        >
          ask about anything. get thoughtful research.
        </p>

        {/* Input form - large and peaceful */}
        <form onSubmit={handleSubmit} style={{ width: '100%' }}>
          <div
            style={{
              position: 'relative',
              marginBottom: '8px',
              opacity: mounted ? 1 : 0.4,
              transform: mounted ? 'scale(1)' : 'scale(0.95)',
              transition: 'all 800ms ease-out 300ms',
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={examples[currentExample]}
              maxLength={300}
              style={{
                width: '100%',
                padding: '16px 18px',
                fontSize: '14px',
                border: `1px solid ${colors.border}`,
                backgroundColor: colors.cardBg,
                borderRadius: '8px',
                fontFamily: 'inherit',
                fontWeight: 300,
                color: colors.text,
                outline: 'none',
                transition: 'all 300ms ease',
                boxShadow: 'none',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = colors.accent;
                e.currentTarget.style.backgroundColor = '#ffffff';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = colors.border;
                e.currentTarget.style.backgroundColor = colors.cardBg;
              }}
              autoFocus
            />
            {/* Character counter */}
            <div
              style={{
                marginTop: '6px',
                fontSize: '10px',
                color: input.length > 250 ? colors.error : colors.textMuted,
                textAlign: 'right',
                opacity: input.length > 0 ? 1 : 0,
                transition: 'all 200ms ease',
              }}
            >
              {input.length} / 300
            </div>
          </div>
          <div style={{ marginBottom: '24px' }} />

          {/* Mode selector - minimal buttons */}
          <div
            style={{
              display: 'flex',
              gap: '12px',
              justifyContent: 'center',
              marginBottom: '32px',
              opacity: mounted ? 0.6 : 0.3,
              transition: 'opacity 800ms ease-out 400ms',
            }}
          >
            <button
              type="button"
              onClick={() => setMode('analytical')}
              style={{
                padding: '6px 12px',
                fontSize: '10px',
                fontWeight: 300,
                backgroundColor: mode === 'analytical' ? colors.primary : 'transparent',
                color: mode === 'analytical' ? '#ffffff' : colors.textLight,
                border: `1px solid ${mode === 'analytical' ? colors.primary : colors.border}`,
                borderRadius: '4px',
                cursor: 'pointer',
                fontFamily: 'inherit',
                transition: 'all 300ms ease',
              }}
            >
              analytical
            </button>
            <button
              type="button"
              onClick={() => setMode('gen-z')}
              style={{
                padding: '6px 12px',
                fontSize: '10px',
                fontWeight: 300,
                backgroundColor: mode === 'gen-z' ? colors.primary : 'transparent',
                color: mode === 'gen-z' ? '#ffffff' : colors.textLight,
                border: `1px solid ${mode === 'gen-z' ? colors.primary : colors.border}`,
                borderRadius: '4px',
                cursor: 'pointer',
                fontFamily: 'inherit',
                transition: 'all 300ms ease',
              }}
            >
              gen-z
            </button>
          </div>

          {/* Submit button - minimal and subtle */}
          <button
            type="submit"
            disabled={!input.trim()}
            style={{
              width: '100%',
              padding: '12px 20px',
              fontSize: '12px',
              fontWeight: 300,
              letterSpacing: '0.5px',
              backgroundColor: input.trim() ? colors.primary : 'transparent',
              color: input.trim() ? '#ffffff' : colors.textMuted,
              border: `1px solid ${input.trim() ? colors.primary : colors.border}`,
              borderRadius: '8px',
              cursor: input.trim() ? 'pointer' : 'not-allowed',
              transition: 'all 400ms ease',
              opacity: input.trim() ? 1 : 0.5,
              fontFamily: 'inherit',
            }}
            onMouseEnter={(e) => {
              if (input.trim()) {
                e.currentTarget.style.opacity = '0.9';
              }
            }}
            onMouseLeave={(e) => {
              if (input.trim()) {
                e.currentTarget.style.opacity = '1';
              }
            }}
          >
            research
          </button>
        </form>

        {/* Spacer for breathing room */}
        <div style={{ height: '60px' }} />
      </div>
    </div>
  );
}
