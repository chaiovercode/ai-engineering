'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { colors } from '@/lib/colors';

interface ResearchItem {
  id: string;
  input: string;
  type: 'topic' | 'url';
  content: string;
  timestamp: number;
}

interface ResearchSidebarProps {
  onSelectResearch: (content: string) => void;
}

export default function ResearchSidebar({ onSelectResearch }: ResearchSidebarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [history, setHistory] = useState<ResearchItem[]>([]);

  useEffect(() => {
    loadHistory();

    const handleResearchSaved = () => {
      loadHistory();
    };

    window.addEventListener('researchSaved', handleResearchSaved);
    return () => window.removeEventListener('researchSaved', handleResearchSaved);
  }, []);

  const loadHistory = () => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('researchHistory');
      if (saved) {
        try {
          setHistory(JSON.parse(saved));
        } catch (err) {
          console.error('Failed to load history:', err);
        }
      }
    }
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = history.filter((item) => item.id !== id);
    localStorage.setItem('researchHistory', JSON.stringify(updated));
    setHistory(updated);
  };

  const router = useRouter();

  const handleSelect = (item: ResearchItem) => {
    router.push(`/chat/${item.id}`);
    setIsOpen(false);
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          top: '10px',
          left: '20px',
          width: '50px',
          height: '50px',
          backgroundColor: colors.primary,
          color: '#ffffff',
          border: 'none',
          borderRadius: '0px',
          cursor: 'pointer',
          fontSize: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 999,
          transition: 'all 200ms ease',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.05)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
        }}
      >
        {isOpen ? '✕' : '≡'}
      </button>

      {/* Sidebar */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: isOpen ? '0px' : '-400px',
          width: '360px',
          height: '100vh',
          backgroundColor: colors.cardBg,
          borderRight: `1px solid ${colors.border}`,
          zIndex: 998,
          overflowY: 'auto',
          transition: 'left 300ms ease',
        }}
      >
        {/* Sidebar header */}
        <div
          style={{
            padding: '20px 20px 20px 20px',
            borderBottom: `1px solid ${colors.border}`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            minHeight: '70px',
          }}
        >
          <h3
            style={{
              fontSize: '14px',
              fontWeight: 400,
              color: colors.text,
              marginLeft: '100px',
            }}
          >
            research history
          </h3>
        </div>

        {/* History items */}
        <div style={{ padding: '16px' }}>
          {history.length === 0 ? (
            <p
              style={{
                fontSize: '13px',
                color: colors.textMuted,
                textAlign: 'center',
                padding: '20px',
              }}
            >
              no research yet
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {history.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleSelect(item)}
                  style={{
                    padding: '12px',
                    backgroundColor: colors.background,
                    border: `1px solid ${colors.border}`,
                    borderRadius: '6px',
                    cursor: 'pointer',
                    transition: 'all 200ms ease',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    gap: '8px',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = colors.surface;
                    e.currentTarget.style.borderColor = colors.primary;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = colors.background;
                    e.currentTarget.style.borderColor = colors.border;
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p
                      style={{
                        fontSize: '13px',
                        fontWeight: 500,
                        color: colors.text,
                        marginBottom: '4px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {item.input}
                    </p>
                    <p
                      style={{
                        fontSize: '12px',
                        color: colors.textMuted,
                      }}
                    >
                      {formatTime(item.timestamp)}
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDelete(item.id, e)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: colors.error,
                      cursor: 'pointer',
                      fontSize: '11px',
                      padding: '4px 6px',
                      fontWeight: 400,
                    }}
                  >
                    del
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Overlay */}
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            zIndex: 997,
          }}
        />
      )}
    </>
  );
}
