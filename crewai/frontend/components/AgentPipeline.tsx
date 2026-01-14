'use client';

import React, { useState, useEffect } from 'react';
import { colors } from '@/lib/colors';

interface Agent {
  name: string;
  status: 'waiting' | 'working' | 'complete' | 'error';
  progress: number;
  message: string;
}

interface AgentPipelineProps {
  agents: Agent[];
  input: string;
}

const getStatusIcon = (status: Agent['status']) => {
  switch (status) {
    case 'complete':
      return '✓';
    case 'working':
      return '◐';
    case 'error':
      return '⚠';
    default:
      return '○';
  }
};

const getStatusColor = (status: Agent['status']) => {
  switch (status) {
    case 'complete':
      return colors.success;
    case 'working':
      return colors.warning;
    case 'error':
      return colors.error;
    default:
      return colors.textMuted;
  }
};

export default function AgentPipeline({ agents, input }: AgentPipelineProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const allComplete = agents.every((a) => a.status === 'complete');
  const completedCount = agents.filter((a) => a.status === 'complete').length;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        padding: '60px 20px 40px',
        backgroundColor: colors.background,
        opacity: mounted ? 1 : 0.9,
        transition: 'opacity 600ms ease-out',
      }}
    >
      <div style={{ width: '100%', maxWidth: '520px' }}>
        {/* Header - minimal and peaceful */}
        <div
          style={{
            marginBottom: '56px',
            textAlign: 'center',
            opacity: mounted ? 1 : 0.6,
            transform: mounted ? 'translateY(0)' : 'translateY(8px)',
            transition: 'all 600ms ease-out 100ms',
          }}
        >
          <h2
            style={{
              fontSize: '24px',
              fontWeight: 300,
              color: colors.text,
              marginBottom: '12px',
              letterSpacing: '0px',
            }}
          >
            researching
          </h2>
          <p
            style={{
              fontSize: '12px',
              color: colors.textLight,
              fontWeight: 300,
              margin: '0',
              lineHeight: '1.6',
              maxWidth: '300px',
              marginLeft: 'auto',
              marginRight: 'auto',
            }}
          >
            {input}
          </p>
        </div>

        {/* Progress overview - subtle indicator */}
        <div
          style={{
            marginBottom: '40px',
            textAlign: 'center',
            opacity: mounted ? 0.6 : 0.3,
            transition: 'opacity 600ms ease-out 200ms',
          }}
        >
          <p
            style={{
              fontSize: '11px',
              color: colors.textMuted,
              fontWeight: 300,
              margin: '0',
            }}
          >
            {completedCount} of {agents.length} {completedCount === 1 ? 'step' : 'steps'} complete
          </p>
        </div>

        {/* Agents - flowing, peaceful layout */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {agents.map((agent, index) => (
            <div
              key={agent.name}
              style={{
                opacity: mounted ? 1 : 0.4,
                transform: mounted ? 'translateY(0)' : 'translateY(12px)',
                transition: `all 600ms ease-out ${150 + index * 80}ms`,
              }}
            >
              {/* Agent card - minimal styling */}
              <div
                style={{
                  backgroundColor: agent.status === 'complete' ? colors.surface : colors.cardBg,
                  border: `1px solid ${
                    agent.status === 'complete' ? colors.success + '20' : colors.border
                  }`,
                  borderRadius: '8px',
                  padding: '18px',
                  transition: 'all 400ms ease',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {/* Subtle background glow for working state */}
                {agent.status === 'working' && (
                  <div
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      background: `linear-gradient(90deg, transparent, ${colors.warning}08, transparent)`,
                      animation: 'pulse 2s ease-in-out infinite',
                      pointerEvents: 'none',
                    }}
                  />
                )}

                {/* Agent header */}
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: agent.message ? '10px' : '0',
                    position: 'relative',
                    zIndex: 1,
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        marginBottom: '6px',
                      }}
                    >
                      <span
                        style={{
                          fontSize: '14px',
                          color: getStatusColor(agent.status),
                          fontWeight: 300,
                          minWidth: '14px',
                          textAlign: 'center',
                          animation:
                            agent.status === 'working' ? 'spin 2s linear infinite' : 'none',
                        }}
                      >
                        {getStatusIcon(agent.status)}
                      </span>
                      <span
                        style={{
                          fontSize: '13px',
                          fontWeight: 400,
                          color: colors.text,
                        }}
                      >
                        {agent.name}
                      </span>
                    </div>

                    {/* Agent message - flowing text */}
                    {agent.message && (
                      <p
                        style={{
                          fontSize: '12px',
                          color: colors.textLight,
                          margin: '0',
                          lineHeight: '1.5',
                          paddingLeft: '24px',
                          fontWeight: 300,
                        }}
                      >
                        {agent.message}
                      </p>
                    )}
                  </div>

                  {/* Status text */}
                  <span
                    style={{
                      fontSize: '10px',
                      color: getStatusColor(agent.status),
                      fontWeight: 300,
                      marginLeft: '12px',
                      marginTop: '2px',
                      whiteSpace: 'nowrap',
                      opacity: agent.status === 'waiting' ? 0.5 : 1,
                      transition: 'opacity 300ms ease',
                    }}
                  >
                    {agent.status === 'complete' && 'complete'}
                    {agent.status === 'working' && `${agent.progress}%`}
                    {agent.status === 'waiting' && 'waiting'}
                    {agent.status === 'error' && 'error'}
                  </span>
                </div>

                {/* Subtle progress indicator - only when working or has progress */}
                {(agent.status === 'working' || (agent.status === 'complete' && agent.progress > 0)) && (
                  <div
                    style={{
                      width: '100%',
                      height: '2px',
                      backgroundColor: colors.surface,
                      borderRadius: '1px',
                      overflow: 'hidden',
                      marginTop: '10px',
                      position: 'relative',
                      zIndex: 1,
                    }}
                  >
                    <div
                      style={{
                        height: '100%',
                        width: `${Math.max(agent.progress, 5)}%`,
                        backgroundColor: getStatusColor(agent.status),
                        borderRadius: '1px',
                        transition: 'width 400ms ease',
                        boxShadow:
                          agent.status === 'working'
                            ? `0 0 6px ${colors.warning}60`
                            : 'none',
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Completion message */}
        {allComplete && (
          <div
            style={{
              marginTop: '40px',
              textAlign: 'center',
              opacity: 0.7,
              animation: 'fadeIn 600ms ease-out',
            }}
          >
            <p
              style={{
                fontSize: '11px',
                color: colors.success,
                fontWeight: 300,
              }}
            >
              all steps complete
            </p>
          </div>
        )}
      </div>

      {/* CSS animations */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0; }
          50% { opacity: 1; }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 0.7; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
