'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { colors } from '@/lib/colors';

interface ResultsDisplayProps {
  content: string;
  onNewSearch: () => void;
}

export default function ResultsDisplay({ content, onNewSearch }: ResultsDisplayProps) {
  // Clean content: remove only outer markdown code block markers, preserve internal markdown
  const cleanedContent = content
    .replace(/^```markdown\n?/i, '') // Remove opening ```markdown
    .replace(/\n?```$/, '') // Remove closing ```
    .trim();

  // Check if content has HTML highlighting
  const hasHTMLHighlighting = cleanedContent.includes('<span style="background-color:');

  // If content has HTML highlighting, render it directly with dangerouslySetInnerHTML
  // Convert markdown-like formatting to HTML
  const renderRawHTML = () => {
    let htmlContent = cleanedContent;

    // First: Convert markdown headers to HTML (must be before paragraph wrapping)
    // Use multiline replacement with proper markers
    htmlContent = htmlContent.replace(/^### (.*?)$/gm, '\n<h3 style="font-size: 16px; font-weight: 400; margin-bottom: 10px; margin-top: 16px; color: #4a423a;">$1</h3>\n');
    htmlContent = htmlContent.replace(/^## (.*?)$/gm, '\n<h2 style="font-size: 20px; font-weight: 400; margin-bottom: 12px; margin-top: 24px; color: #4a423a;">$1</h2>\n');
    htmlContent = htmlContent.replace(/^# (.*?)$/gm, '\n<h1 style="font-size: 24px; font-weight: 400; margin-bottom: 16px; margin-top: 0; color: #4a423a;">$1</h1>\n');

    // Convert markdown bold to HTML
    htmlContent = htmlContent.replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: 600;">$1</strong>');

    // Convert markdown italic to HTML
    htmlContent = htmlContent.replace(/\*(.*?)\*/g, '<em style="font-style: italic;">$1</em>');

    // Process line by line instead of paragraph by paragraph
    const lines = htmlContent.split('\n');
    const result: string[] = [];
    let currentParagraph: string[] = [];

    for (const line of lines) {
      const trimmed = line.trim();

      // If it's a header or empty, flush current paragraph and add the line
      if (trimmed.startsWith('<h') || trimmed === '') {
        if (currentParagraph.length > 0) {
          const paragraphText = currentParagraph.join(' ').trim();
          if (paragraphText && !paragraphText.startsWith('<')) {
            result.push(`<p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">${paragraphText}</p>`);
          }
          currentParagraph = [];
        }
        if (trimmed) {
          result.push(trimmed);
        }
      } else if (trimmed) {
        // Add to current paragraph
        currentParagraph.push(trimmed);
      }
    }

    // Flush remaining paragraph
    if (currentParagraph.length > 0) {
      const paragraphText = currentParagraph.join(' ').trim();
      if (paragraphText && !paragraphText.startsWith('<')) {
        result.push(`<p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">${paragraphText}</p>`);
      }
    }

    return result.join('');
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(cleanedContent);
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
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        padding: '20px 20px 40px 20px',
        backgroundColor: colors.background,
        minHeight: '100vh',
      }}
    >
      <div style={{ width: '100%', maxWidth: '900px' }}>
        {/* Content card */}
        <div
          style={{
            backgroundColor: colors.cardBg,
            border: `1px solid ${colors.border}`,
            borderRadius: '8px',
            padding: '32px 40px',
            marginBottom: '24px',
          }}
        >
          {/* Always render as HTML to ensure headers display correctly */}
          <div
            style={{
              fontSize: '14px',
              lineHeight: '1.8',
              color: colors.text,
              wordWrap: 'break-word',
              overflowWrap: 'break-word',
              wordBreak: 'break-word',
            }}
            dangerouslySetInnerHTML={{ __html: renderRawHTML() }}
          />
        </div>

        {/* Navigation and Action buttons */}
        <div
          style={{
            display: 'flex',
            gap: '12px',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            marginBottom: '0',
          }}
        >
          <div
            style={{
              display: 'flex',
              gap: '12px',
            }}
          >
          <button
            onClick={handleCopy}
            style={{
              padding: '10px 18px',
              fontSize: '12px',
              backgroundColor: colors.primary,
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontFamily: 'inherit',
              fontWeight: 400,
              transition: 'all 200ms ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translate(2px, 2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translate(0, 0)';
            }}
          >
            copy
          </button>
          <button
            onClick={handleDownload}
            style={{
              padding: '10px 18px',
              fontSize: '12px',
              backgroundColor: colors.accent,
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontFamily: 'inherit',
              fontWeight: 400,
              transition: 'all 200ms ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translate(2px, 2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translate(0, 0)';
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
              padding: '10px 18px',
              fontSize: '12px',
              backgroundColor: colors.accent,
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontFamily: 'inherit',
              fontWeight: 400,
              transition: 'all 200ms ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translate(2px, 2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translate(0, 0)';
            }}
          >
            share
          </button>
          </div>

          <button
            onClick={onNewSearch}
            style={{
              padding: '10px 16px',
              fontSize: '12px',
              backgroundColor: 'transparent',
              color: colors.accent,
              border: `1px solid ${colors.accent}`,
              borderRadius: '6px',
              cursor: 'pointer',
              fontFamily: 'inherit',
              transition: 'all 200ms ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = colors.accent;
              e.currentTarget.style.color = '#ffffff';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = colors.accent;
            }}
          >
            new research
          </button>
        </div>
      </div>
    </div>
  );
}
