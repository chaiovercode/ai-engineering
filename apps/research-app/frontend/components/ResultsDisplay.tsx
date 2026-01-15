'use client';

import React, { useState, useEffect } from 'react';
import { colors } from '@/lib/colors';

interface ResultsDisplayProps {
  content: string;
  onNewSearch: () => void;
}

export default function ResultsDisplay({ content, onNewSearch }: ResultsDisplayProps) {
  const [mounted, setMounted] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Guard against undefined content
  if (!content) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          backgroundColor: colors.background,
        }}
      >
        <p
          style={{
            fontFamily: '"Cormorant Garamond", Georgia, serif',
            fontSize: '16px',
            fontStyle: 'italic',
            color: colors.textMuted,
          }}
        >
          preparing your research...
        </p>
      </div>
    );
  }

  // Clean content: remove only outer markdown code block markers, preserve internal markdown
  const cleanedContent = content
    .replace(/^```markdown\n?/i, '')
    .replace(/\n?```$/, '')
    .trim();

  // Convert markdown to styled HTML with The Study aesthetic
  const renderRawHTML = () => {
    // Normalize line endings
    const normalized = cleanedContent.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const lines = normalized.split('\n');
    const result: string[] = [];
    let currentParagraph: string[] = [];
    let inList = false;
    let listItems: string[] = [];

    // Styles as constants for cleaner code
    const styles = {
      h1: `font-family: 'Cormorant Garamond', Georgia, serif; font-size: 34px; font-weight: 300; margin-bottom: 24px; margin-top: 8px; color: ${colors.text}; letter-spacing: 0.02em; line-height: 1.3; border-bottom: 1px solid ${colors.border}; padding-bottom: 16px;`,
      h2: `font-family: 'Cormorant Garamond', Georgia, serif; font-size: 26px; font-weight: 400; margin-bottom: 16px; margin-top: 40px; color: ${colors.text}; letter-spacing: 0.02em; line-height: 1.3;`,
      h3: `font-family: 'Cormorant Garamond', Georgia, serif; font-size: 20px; font-weight: 500; margin-bottom: 12px; margin-top: 32px; color: ${colors.text}; letter-spacing: 0.02em; line-height: 1.4;`,
      h4: `font-family: 'Cormorant Garamond', Georgia, serif; font-size: 18px; font-weight: 500; margin-bottom: 10px; margin-top: 24px; color: ${colors.text}; letter-spacing: 0.02em; line-height: 1.4;`,
      p: `font-family: 'Outfit', sans-serif; font-size: 17px; font-weight: 300; margin-bottom: 18px; line-height: 1.85; color: ${colors.textLight};`,
      li: `font-family: 'Outfit', sans-serif; font-size: 17px; font-weight: 300; line-height: 1.85; color: ${colors.textLight}; margin-bottom: 8px; padding-left: 8px;`,
      ul: `list-style: none; margin: 0 0 24px 0; padding-left: 20px;`,
      strong: `font-weight: 500; color: ${colors.text};`,
    };

    const flushParagraph = () => {
      if (currentParagraph.length > 0) {
        const text = currentParagraph.join(' ').trim();
        if (text) {
          result.push(`<p style="${styles.p}">${text}</p>`);
        }
        currentParagraph = [];
      }
    };

    const flushList = () => {
      if (listItems.length > 0) {
        const items = listItems.map(item =>
          `<li style="${styles.li}"><span style="color: ${colors.accent}; margin-right: 12px;">•</span>${item}</li>`
        ).join('');
        result.push(`<ul style="${styles.ul}">${items}</ul>`);
        listItems = [];
        inList = false;
      }
    };

    const processInlineFormatting = (text: string): string => {
      return text
        .replace(/\*\*(.+?)\*\*/g, `<strong style="${styles.strong}">$1</strong>`)
        .replace(/\*(.+?)\*/g, '<em style="font-style: italic;">$1</em>')
        .replace(/`(.+?)`/g, `<code style="background: ${colors.surface}; padding: 2px 6px; border-radius: 3px; font-size: 13px; color: ${colors.accent};">$1</code>`);
    };

    for (const line of lines) {
      const trimmed = line.trim();

      // Check for headers (# ## ### ####) - check longer patterns first
      const h4Match = trimmed.match(/^####\s+(.+)$/);
      const h3Match = trimmed.match(/^###\s+(.+)$/);
      const h2Match = trimmed.match(/^##\s+(.+)$/);
      const h1Match = trimmed.match(/^#\s+(.+)$/);

      // Check for list items
      const listMatch = trimmed.match(/^[-*]\s+(.+)$/);

      if (h4Match) {
        flushParagraph();
        flushList();
        result.push(`<h4 style="${styles.h4}">${processInlineFormatting(h4Match[1])}</h4>`);
      } else if (h3Match) {
        flushParagraph();
        flushList();
        result.push(`<h3 style="${styles.h3}">${processInlineFormatting(h3Match[1])}</h3>`);
      } else if (h2Match) {
        flushParagraph();
        flushList();
        result.push(`<h2 style="${styles.h2}">${processInlineFormatting(h2Match[1])}</h2>`);
      } else if (h1Match) {
        flushParagraph();
        flushList();
        result.push(`<h1 style="${styles.h1}">${processInlineFormatting(h1Match[1])}</h1>`);
      } else if (listMatch) {
        flushParagraph();
        inList = true;
        listItems.push(processInlineFormatting(listMatch[1]));
      } else if (trimmed === '') {
        flushParagraph();
        if (inList) flushList();
      } else {
        if (inList) flushList();
        currentParagraph.push(processInlineFormatting(trimmed));
      }
    }

    // Flush any remaining content
    flushParagraph();
    flushList();

    return result.join('');
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(cleanedContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([cleanedContent], { type: 'text/markdown' });
    element.href = URL.createObjectURL(file);
    element.download = `research-${Date.now()}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <>
{/* Fonts and animations defined in globals.css */}

      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          padding: '20px 24px 60px',
          backgroundColor: colors.background,
          minHeight: '100vh',
        }}
      >
        <div
          style={{
            width: '100%',
            maxWidth: '792px',
            opacity: mounted ? 1 : 0,
            transform: mounted ? 'translateY(0)' : 'translateY(16px)',
            transition: 'all 0.8s ease-out',
          }}
        >
          {/* Decorative header */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '16px',
              marginBottom: '40px',
            }}
          >
            <div style={{ width: '40px', height: '1px', backgroundColor: colors.border }} />
            <span
              style={{
                fontFamily: '"Outfit", sans-serif',
                fontSize: '11px',
                letterSpacing: '0.2em',
                textTransform: 'uppercase',
                color: colors.textMuted,
              }}
            >
              research complete
            </span>
            <div style={{ width: '40px', height: '1px', backgroundColor: colors.border }} />
          </div>

          {/* Content card */}
          <div
            style={{
              backgroundColor: colors.cardBg,
              border: `1px solid ${colors.border}`,
              borderRadius: '3px',
              padding: '48px 40px',
              marginBottom: '32px',
              position: 'relative',
            }}
          >
            {/* Corner accent */}
            <div
              style={{
                position: 'absolute',
                top: '16px',
                left: '16px',
                width: '24px',
                height: '24px',
                borderLeft: `1px solid ${colors.accent}40`,
                borderTop: `1px solid ${colors.accent}40`,
              }}
            />
            <div
              style={{
                position: 'absolute',
                bottom: '16px',
                right: '16px',
                width: '24px',
                height: '24px',
                borderRight: `1px solid ${colors.accent}40`,
                borderBottom: `1px solid ${colors.accent}40`,
              }}
            />

            <div
              style={{
                wordWrap: 'break-word',
                overflowWrap: 'break-word',
                wordBreak: 'break-word',
              }}
              dangerouslySetInnerHTML={{ __html: renderRawHTML() }}
            />
          </div>

          {/* Action buttons */}
          <div
            style={{
              display: 'flex',
              gap: '12px',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
            }}
          >
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={handleCopy}
                style={{
                  padding: '10px 20px',
                  fontFamily: '"Outfit", sans-serif',
                  fontSize: '12px',
                  fontWeight: 400,
                  letterSpacing: '0.08em',
                  backgroundColor: 'transparent',
                  color: copied ? colors.success : colors.textLight,
                  border: `1px solid ${copied ? colors.success + '60' : colors.border}`,
                  borderRadius: '2px',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                }}
              >
                {copied ? 'copied' : 'copy'}
              </button>
              <button
                onClick={handleDownload}
                style={{
                  padding: '10px 20px',
                  fontFamily: '"Outfit", sans-serif',
                  fontSize: '12px',
                  fontWeight: 400,
                  letterSpacing: '0.08em',
                  backgroundColor: 'transparent',
                  color: colors.textLight,
                  border: `1px solid ${colors.border}`,
                  borderRadius: '2px',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                }}
              >
                download
              </button>
              <button
                onClick={() => {
                  const url = typeof window !== 'undefined' ? window.location.href : '';
                  navigator.clipboard.writeText(url);
                }}
                style={{
                  padding: '10px 20px',
                  fontFamily: '"Outfit", sans-serif',
                  fontSize: '12px',
                  fontWeight: 400,
                  letterSpacing: '0.08em',
                  backgroundColor: 'transparent',
                  color: colors.textLight,
                  border: `1px solid ${colors.border}`,
                  borderRadius: '2px',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                }}
              >
                share
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
