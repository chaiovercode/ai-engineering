'use client';

import React, { useEffect } from 'react';
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
    htmlContent = htmlContent.replace(/^### (.*?)$/gm, '<h3 style="font-size: 16px; font-weight: 400; margin-bottom: 10px; margin-top: 16px; color: #4a423a;">$1</h3>');
    htmlContent = htmlContent.replace(/^## (.*?)$/gm, '<h2 style="font-size: 20px; font-weight: 400; margin-bottom: 12px; margin-top: 24px; color: #4a423a;">$1</h2>');
    htmlContent = htmlContent.replace(/^# (.*?)$/gm, '<h1 style="font-size: 24px; font-weight: 400; margin-bottom: 16px; margin-top: 0; color: #4a423a;">$1</h1>');

    // Convert markdown bold to HTML
    htmlContent = htmlContent.replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: 600;">$1</strong>');

    // Convert markdown italic to HTML
    htmlContent = htmlContent.replace(/\*(.*?)\*/g, '<em style="font-style: italic;">$1</em>');

    // Convert line breaks into proper HTML structure
    // Split by double newlines to handle paragraphs
    const paragraphs = htmlContent.split(/\n\n+/).map((p) => {
      // Skip if this is a header
      if (p.trim().startsWith('<h')) {
        return p.trim();
      }
      // Wrap regular text in paragraph tags
      return `<p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">${p.trim()}</p>`;
    });

    return paragraphs.join('');
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
          {hasHTMLHighlighting ? (
            // Render HTML content directly with dangerouslySetInnerHTML
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
          ) : (
            // Render markdown content with ReactMarkdown
            <div
              style={{
                fontSize: '14px',
                lineHeight: '1.8',
                color: colors.text,
                wordWrap: 'break-word',
                overflowWrap: 'break-word',
                wordBreak: 'break-word',
              }}
            >
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                skipHtml={false}
                allowHtml={true}
                components={{
                h1: ({ children }) => (
                  <h1 style={{ fontSize: '24px', fontWeight: 400, marginBottom: '16px', marginTop: '0', color: colors.text }}>
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 style={{ fontSize: '20px', fontWeight: 400, marginBottom: '12px', marginTop: '24px', color: colors.text }}>
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 style={{ fontSize: '16px', fontWeight: 400, marginBottom: '10px', marginTop: '16px', color: colors.text }}>
                    {children}
                  </h3>
                ),
                h4: ({ children }) => (
                  <h4 style={{ fontSize: '14px', fontWeight: 400, marginBottom: '8px', marginTop: '12px', color: colors.text }}>
                    {children}
                  </h4>
                ),
                p: ({ children, node }) => {
                  // Check if paragraph contains HTML (highlight spans)
                  const hasHtml = node?.children?.some((child: any) => child.type === 'html');

                  if (hasHtml) {
                    // Render HTML content with dangerouslySetInnerHTML
                    const htmlContent = node?.children
                      ?.map((child: any) => {
                        if (child.type === 'html') return child.value;
                        if (child.type === 'text') return child.value;
                        return '';
                      })
                      .join('') || '';

                    return (
                      <p
                        style={{ marginBottom: '12px', lineHeight: '1.8', textAlign: 'justify' }}
                        dangerouslySetInnerHTML={{ __html: htmlContent }}
                      />
                    );
                  }

                  return (
                    <p style={{ marginBottom: '12px', lineHeight: '1.8', textAlign: 'justify' }}>
                      {children}
                    </p>
                  );
                },
                ul: ({ children }) => (
                  <ul style={{ marginBottom: '12px', paddingLeft: '20px', listStyle: 'none' }}>
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol style={{ marginBottom: '12px', paddingLeft: '20px', listStyle: 'decimal' }}>
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li style={{ marginBottom: '6px', paddingLeft: '4px' }}>
                    {children}
                  </li>
                ),
                strong: ({ children }) => (
                  <strong style={{ fontWeight: 600 }}>
                    {children}
                  </strong>
                ),
                em: ({ children }) => (
                  <em style={{ fontStyle: 'italic' }}>
                    {children}
                  </em>
                ),
                code: ({ children }) => (
                  <code style={{ backgroundColor: colors.surface, padding: '2px 6px', borderRadius: '4px', fontSize: '13px' }}>
                    {children}
                  </code>
                ),
                pre: ({ children }) => (
                  <pre style={{ backgroundColor: colors.surface, padding: '12px', borderRadius: '6px', overflow: 'auto', marginBottom: '12px', fontSize: '12px' }}>
                    {children}
                  </pre>
                ),
                blockquote: ({ children }) => (
                  <blockquote style={{ borderLeft: `3px solid ${colors.accent}`, paddingLeft: '12px', marginLeft: '0', marginBottom: '12px', color: colors.textLight, fontStyle: 'italic' }}>
                    {children}
                  </blockquote>
                ),
                html: ({ value }) => {
                  // Handle inline HTML like <span> tags for highlighting
                  return <span dangerouslySetInnerHTML={{ __html: value }} style={{ display: 'inline' }} />;
                },
              }}
            >
              {cleanedContent}
              </ReactMarkdown>
            </div>
          )}
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
