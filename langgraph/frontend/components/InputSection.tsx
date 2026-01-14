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
  const [focused, setFocused] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentExample((prev) => (prev + 1) % examples.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const detectType = (text: string): 'topic' | 'url' => {
    return text.startsWith('http://') || text.startsWith('https://') ? 'url' : 'topic';
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSubmit(input.trim(), detectType(input.trim()), mode);
    }
  };

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: `
        .study-input::placeholder {
          color: ${colors.textMuted};
          font-style: italic;
          opacity: 0.7;
        }
        .study-input:focus {
          outline: none;
        }
      `}} />

      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          padding: '40px 24px',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Subtle ambient glow */}
        <div
          style={{
            position: 'absolute',
            top: '20%',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '600px',
            height: '400px',
            background: `radial-gradient(ellipse, ${colors.accent}08 0%, transparent 70%)`,
            pointerEvents: 'none',
            animation: 'warmGlow 8s ease-in-out infinite',
          }}
        />

        <div
          style={{
            width: '100%',
            maxWidth: '440px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            position: 'relative',
            zIndex: 1,
          }}
        >
          {/* Decorative line */}
          <div
            style={{
              width: '40px',
              height: '1px',
              background: `linear-gradient(90deg, transparent, ${colors.accent}60, transparent)`,
              marginBottom: '48px',
              opacity: mounted ? 1 : 0,
              transition: 'opacity 1.2s ease-out',
            }}
          />

          {/* Title - Editorial serif */}
          <h1
            style={{
              fontFamily: '"Cormorant Garamond", Georgia, serif',
              fontSize: '42px',
              fontWeight: 300,
              marginBottom: '16px',
              color: colors.text,
              letterSpacing: '0.02em',
              lineHeight: '1.1',
              opacity: mounted ? 1 : 0,
              transform: mounted ? 'translateY(0)' : 'translateY(16px)',
              transition: 'all 1s ease-out 0.1s',
            }}
          >
            zensar research
          </h1>

          {/* Tagline - Elegant italic */}
          <p
            style={{
              fontFamily: '"Cormorant Garamond", Georgia, serif',
              fontSize: '16px',
              fontStyle: 'italic',
              color: colors.textLight,
              fontWeight: 300,
              marginBottom: '64px',
              lineHeight: '1.6',
              opacity: mounted ? 0.8 : 0,
              transition: 'opacity 1s ease-out 0.3s',
              letterSpacing: '0.02em',
            }}
          >
            thoughtful inquiry, meaningful answers
          </p>

          {/* Input form */}
          <form onSubmit={handleSubmit} style={{ width: '100%' }}>
            <div
              style={{
                position: 'relative',
                marginBottom: '32px',
                opacity: mounted ? 1 : 0,
                transform: mounted ? 'translateY(0)' : 'translateY(12px)',
                transition: 'all 1s ease-out 0.4s',
              }}
            >
              {/* Input glow effect when focused */}
              <div
                style={{
                  position: 'absolute',
                  inset: '-1px',
                  borderRadius: '4px',
                  background: `linear-gradient(135deg, ${colors.accent}30, transparent, ${colors.accent}20)`,
                  opacity: focused ? 1 : 0,
                  transition: 'opacity 0.4s ease',
                  pointerEvents: 'none',
                }}
              />

              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                placeholder={examples[currentExample]}
                maxLength={300}
                className="study-input"
                style={{
                  width: '100%',
                  padding: '18px 20px',
                  fontFamily: '"Outfit", sans-serif',
                  fontSize: '15px',
                  fontWeight: 300,
                  border: `1px solid ${focused ? colors.accent + '60' : colors.border}`,
                  backgroundColor: colors.cardBg,
                  borderRadius: '4px',
                  color: colors.text,
                  transition: 'all 0.4s ease',
                  letterSpacing: '0.01em',
                  position: 'relative',
                }}
                autoFocus
              />

              {/* Character counter */}
              <div
                style={{
                  position: 'absolute',
                  right: '12px',
                  bottom: '-24px',
                  fontFamily: '"Outfit", sans-serif',
                  fontSize: '11px',
                  color: input.length > 250 ? colors.error : colors.textMuted,
                  opacity: input.length > 0 ? 0.6 : 0,
                  transition: 'all 0.3s ease',
                  letterSpacing: '0.05em',
                }}
              >
                {input.length}/300
              </div>
            </div>

            {/* Mode selector - Refined pills */}
            <div
              style={{
                display: 'flex',
                gap: '8px',
                justifyContent: 'center',
                marginBottom: '40px',
                opacity: mounted ? 1 : 0,
                transition: 'opacity 1s ease-out 0.5s',
              }}
            >
              {(['analytical', 'gen-z'] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setMode(m)}
                  style={{
                    padding: '8px 20px',
                    fontFamily: '"Outfit", sans-serif',
                    fontSize: '12px',
                    fontWeight: 400,
                    letterSpacing: '0.08em',
                    textTransform: 'lowercase',
                    backgroundColor: mode === m ? colors.accent + '20' : 'transparent',
                    color: mode === m ? colors.accent : colors.textMuted,
                    border: `1px solid ${mode === m ? colors.accent + '40' : colors.border}`,
                    borderRadius: '2px',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                  }}
                >
                  {m}
                </button>
              ))}
            </div>

            {/* Submit button - Elegant CTA */}
            <button
              type="submit"
              disabled={!input.trim()}
              style={{
                width: '100%',
                padding: '16px 24px',
                fontFamily: '"Cormorant Garamond", Georgia, serif',
                fontSize: '16px',
                fontWeight: 400,
                letterSpacing: '0.15em',
                textTransform: 'lowercase',
                backgroundColor: input.trim() ? colors.accent : 'transparent',
                color: input.trim() ? colors.background : colors.textMuted,
                border: `1px solid ${input.trim() ? colors.accent : colors.border}`,
                borderRadius: '2px',
                cursor: input.trim() ? 'pointer' : 'default',
                transition: 'all 0.5s ease',
                opacity: mounted ? 1 : 0,
                transform: mounted ? 'translateY(0)' : 'translateY(8px)',
              }}
              onMouseEnter={(e) => {
                if (input.trim()) {
                  e.currentTarget.style.backgroundColor = colors.primary;
                  e.currentTarget.style.borderColor = colors.primary;
                }
              }}
              onMouseLeave={(e) => {
                if (input.trim()) {
                  e.currentTarget.style.backgroundColor = colors.accent;
                  e.currentTarget.style.borderColor = colors.accent;
                }
              }}
            >
              begin research
            </button>
          </form>

          {/* Bottom decorative element */}
          <div
            style={{
              marginTop: '80px',
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
              opacity: mounted ? 0.4 : 0,
              transition: 'opacity 1.2s ease-out 0.8s',
            }}
          >
            <div style={{ width: '24px', height: '1px', backgroundColor: colors.border }} />
            <span
              style={{
                fontFamily: '"Cormorant Garamond", Georgia, serif',
                fontSize: '12px',
                fontStyle: 'italic',
                color: colors.textMuted,
                letterSpacing: '0.1em',
              }}
            >
              powered by ai agents
            </span>
            <div style={{ width: '24px', height: '1px', backgroundColor: colors.border }} />
          </div>
        </div>
      </div>
    </>
  );
}
