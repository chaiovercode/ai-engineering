'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { colors } from '@/lib/colors';
import { fetchHistory, deleteResearch } from '@/lib/api';

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

export default function ResearchSidebar({ onSelectResearch: _onSelectResearch }: ResearchSidebarProps) {
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

  const loadHistory = async () => {
    try {
      const { items } = await fetchHistory();
      setHistory(items);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const success = await deleteResearch(id);
    if (success) {
      const updated = history.filter((item) => item.id !== id);
      setHistory(updated);
    }
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
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    if (diffDays < 7) return `${diffDays}d`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <>
      {/* Toggle button - only visible when sidebar closed */}
      {!isOpen && (
        <>
          <button
            onClick={() => setIsOpen(true)}
            style={{
              position: 'fixed',
              top: '20px',
              left: '20px',
              width: '40px',
              height: '40px',
              backgroundColor: 'transparent',
              color: colors.textMuted,
              border: `1px solid ${colors.border}`,
              borderRadius: '2px',
              cursor: 'pointer',
              fontFamily: '"Outfit", sans-serif',
              fontSize: '16px',
              fontWeight: 300,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 999,
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = colors.accent;
              e.currentTarget.style.color = colors.accent;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = colors.border;
              e.currentTarget.style.color = colors.textMuted;
            }}
          >
            ☰
          </button>

          {/* New inquiry button - below hamburger when collapsed */}
          <button
            onClick={() => router.push('/')}
            style={{
              position: 'fixed',
              top: '70px',
              left: '20px',
              width: '40px',
              height: '40px',
              backgroundColor: colors.accent,
              color: colors.background,
              border: 'none',
              borderRadius: '2px',
              cursor: 'pointer',
              fontFamily: '"Outfit", sans-serif',
              fontSize: '22px',
              fontWeight: 300,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 999,
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = '0.85';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = '1';
            }}
          >
            +
          </button>
        </>
      )}

      {/* Sidebar */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: isOpen ? '0px' : '-340px',
          width: '320px',
          height: '100vh',
          backgroundColor: colors.cardBg,
          borderRight: `1px solid ${colors.border}`,
          zIndex: 998,
          overflowY: 'auto',
          transition: 'left 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        }}
      >
        {/* Sidebar top bar with close and new buttons */}
        <div
          style={{
            padding: '20px 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          {/* Close button */}
          <button
            onClick={() => setIsOpen(false)}
            style={{
              width: '40px',
              height: '40px',
              backgroundColor: 'transparent',
              color: colors.textMuted,
              border: `1px solid ${colors.border}`,
              borderRadius: '2px',
              cursor: 'pointer',
              fontFamily: '"Outfit", sans-serif',
              fontSize: '18px',
              fontWeight: 300,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = colors.accent;
              e.currentTarget.style.color = colors.accent;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = colors.border;
              e.currentTarget.style.color = colors.textMuted;
            }}
          >
            ×
          </button>

          {/* New inquiry button */}
          <button
            onClick={() => {
              router.push('/');
              setIsOpen(false);
            }}
            style={{
              width: '40px',
              height: '40px',
              backgroundColor: colors.accent,
              color: colors.background,
              border: 'none',
              borderRadius: '2px',
              cursor: 'pointer',
              fontFamily: '"Outfit", sans-serif',
              fontSize: '22px',
              fontWeight: 300,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = '0.85';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = '1';
            }}
          >
            +
          </button>
        </div>

        {/* Sidebar header */}
        <div
          style={{
            padding: '16px 24px',
          }}
        >
          <p
            style={{
              fontFamily: '"Outfit", sans-serif',
              fontSize: '12px',
              fontWeight: 400,
              color: colors.textMuted,
              letterSpacing: '0.05em',
            }}
          >
            past inquiries
          </p>
        </div>

        {/* History items */}
        <div style={{ padding: '20px' }}>
          {history.length === 0 ? (
            <div
              style={{
                textAlign: 'center',
                padding: '40px 20px',
              }}
            >
              <p
                style={{
                  fontFamily: '"Cormorant Garamond", Georgia, serif',
                  fontSize: '14px',
                  fontStyle: 'italic',
                  color: colors.textMuted,
                  marginBottom: '8px',
                }}
              >
                no research yet
              </p>
              <p
                style={{
                  fontFamily: '"Outfit", sans-serif',
                  fontSize: '11px',
                  color: colors.textMuted,
                  opacity: 0.6,
                }}
              >
                your inquiries will appear here
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {history.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleSelect(item)}
                  style={{
                    padding: '14px 16px',
                    backgroundColor: 'transparent',
                    border: `1px solid ${colors.border}`,
                    borderRadius: '2px',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '12px',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = colors.background;
                    e.currentTarget.style.borderColor = colors.accent + '40';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.borderColor = colors.border;
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p
                      style={{
                        fontFamily: '"Outfit", sans-serif',
                        fontSize: '13px',
                        fontWeight: 400,
                        color: colors.text,
                        marginBottom: '4px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        letterSpacing: '0.01em',
                      }}
                    >
                      {item.input}
                    </p>
                    <p
                      style={{
                        fontFamily: '"Outfit", sans-serif',
                        fontSize: '11px',
                        color: colors.textMuted,
                        letterSpacing: '0.05em',
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
                      fontFamily: '"Outfit", sans-serif',
                      color: colors.textMuted,
                      cursor: 'pointer',
                      fontSize: '10px',
                      padding: '4px 8px',
                      fontWeight: 400,
                      letterSpacing: '0.1em',
                      opacity: 0.5,
                      transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.color = colors.error;
                      e.currentTarget.style.opacity = '1';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.color = colors.textMuted;
                      e.currentTarget.style.opacity = '0.5';
                    }}
                  >
                    remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar footer */}
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            padding: '20px 24px',
            borderTop: `1px solid ${colors.border}`,
            backgroundColor: colors.cardBg,
          }}
        >
          <p
            style={{
              fontFamily: '"Outfit", sans-serif',
              fontSize: '10px',
              color: colors.textMuted,
              textAlign: 'center',
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              opacity: 0.5,
            }}
          >
            zensar research
          </p>
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
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            zIndex: 997,
            transition: 'opacity 0.3s ease',
          }}
        />
      )}
    </>
  );
}
