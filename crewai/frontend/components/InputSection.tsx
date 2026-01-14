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

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentExample((prev) => (prev + 1) % examples.length);
    }, 4000);
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
        justifyContent: 'center',
        alignItems: 'center',
        height: 'calc(100vh - 80px)',
        paddingLeft: '20px',
        paddingRight: '20px',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '550px',
        }}
      >
        {/* Hero text */}
        <div
          style={{
            textAlign: 'center',
            marginBottom: '24px',
          }}
        >
          <h1
            style={{
              fontSize: '26px',
              fontWeight: 400,
              marginBottom: '6px',
              color: colors.text,
              letterSpacing: '-0.3px',
            }}
          >
            zensar research
          </h1>
          <p
            style={{
              fontSize: '11px',
              color: colors.textLight,
              fontWeight: 400,
              marginBottom: '0',
              lineHeight: '1.5',
            }}
          >
            input a topic or url for ai-powered research writeups.
          </p>
        </div>

        {/* Input form */}
        <form onSubmit={handleSubmit}>
          <div
            style={{
              position: 'relative',
              marginBottom: '12px',
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={examples[currentExample]}
              style={{
                width: '100%',
                padding: '9px 12px',
                fontSize: '13px',
                border: `1px solid ${colors.border}`,
                backgroundColor: colors.cardBg,
                borderRadius: '6px',
                fontFamily: 'inherit',
                color: colors.text,
                outline: 'none',
                transition: 'all 200ms ease',
                boxShadow: `0 0 0 0 transparent`,
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = colors.accent;
                e.currentTarget.style.boxShadow = `0 0 0 2px rgba(160, 176, 154, 0.1)`;
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = colors.border;
                e.currentTarget.style.boxShadow = `0 0 0 0 transparent`;
              }}
              autoFocus
            />
          </div>

          {/* Mode selector */}
          <div
            style={{
              display: 'flex',
              gap: '10px',
              marginBottom: '12px',
            }}
          >
            <button
              type="button"
              onClick={() => setMode('analytical')}
              style={{
                flex: 1,
                padding: '8px 12px',
                fontSize: '11px',
                fontWeight: 400,
                backgroundColor: mode === 'analytical' ? colors.primary : colors.cardBg,
                color: mode === 'analytical' ? '#ffffff' : colors.text,
                border: `1px solid ${mode === 'analytical' ? colors.primary : colors.border}`,
                borderRadius: '6px',
                cursor: 'pointer',
                fontFamily: 'inherit',
                transition: 'all 200ms ease',
              }}
              onMouseEnter={(e) => {
                if (mode !== 'analytical') {
                  e.currentTarget.style.borderColor = colors.primary;
                }
              }}
              onMouseLeave={(e) => {
                if (mode !== 'analytical') {
                  e.currentTarget.style.borderColor = colors.border;
                }
              }}
            >
              analytical
            </button>
            <button
              type="button"
              onClick={() => setMode('gen-z')}
              style={{
                flex: 1,
                padding: '8px 12px',
                fontSize: '11px',
                fontWeight: 400,
                backgroundColor: mode === 'gen-z' ? colors.primary : colors.cardBg,
                color: mode === 'gen-z' ? '#ffffff' : colors.text,
                border: `1px solid ${mode === 'gen-z' ? colors.primary : colors.border}`,
                borderRadius: '6px',
                cursor: 'pointer',
                fontFamily: 'inherit',
                transition: 'all 200ms ease',
              }}
              onMouseEnter={(e) => {
                if (mode !== 'gen-z') {
                  e.currentTarget.style.borderColor = colors.primary;
                }
              }}
              onMouseLeave={(e) => {
                if (mode !== 'gen-z') {
                  e.currentTarget.style.borderColor = colors.border;
                }
              }}
            >
              gen-z
            </button>
          </div>

          <button
            type="submit"
            disabled={!input.trim()}
            style={{
              width: '100%',
              padding: '9px 16px',
              fontSize: '12px',
              fontWeight: 400,
              backgroundColor: input.trim() ? colors.primary : colors.textMuted,
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              cursor: input.trim() ? 'pointer' : 'not-allowed',
              transition: 'all 200ms ease',
              opacity: input.trim() ? 1 : 0.5,
              fontFamily: 'inherit',
            }}
            onMouseEnter={(e) => {
              if (input.trim()) {
                e.currentTarget.style.transform = 'translate(2px, 2px)';
                e.currentTarget.style.boxShadow = 'none';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translate(0, 0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            generate research
          </button>
        </form>
      </div>
    </div>
  );
}
