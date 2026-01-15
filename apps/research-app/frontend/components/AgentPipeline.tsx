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
      return '•';
    case 'working':
      return '○';
    case 'error':
      return '×';
    default:
      return '·';
  }
};

export default function AgentPipeline({ agents, input }: AgentPipelineProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const allComplete = agents.every((a) => a.status === 'complete');

  return (
    <>
{/* Animations defined in globals.css */}

      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          padding: '60px 24px 40px',
          backgroundColor: colors.background,
          position: 'relative',
        }}
      >
        {/* Ambient background glow */}
        <div
          style={{
            position: 'absolute',
            top: '30%',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '500px',
            height: '300px',
            background: `radial-gradient(ellipse, ${colors.warning}06 0%, transparent 70%)`,
            pointerEvents: 'none',
            animation: 'gentlePulse 4s ease-in-out infinite',
          }}
        />

        <div style={{ width: '100%', maxWidth: '500px', position: 'relative', zIndex: 1 }}>
          {/* Header */}
          <div
            style={{
              marginBottom: '48px',
              textAlign: 'center',
              opacity: mounted ? 1 : 0,
              transform: mounted ? 'translateY(0)' : 'translateY(12px)',
              transition: 'all 0.8s ease-out',
            }}
          >
            <p
              style={{
                fontFamily: '"Outfit", sans-serif',
                fontSize: '11px',
                letterSpacing: '0.2em',
                textTransform: 'uppercase',
                color: colors.textMuted,
                marginBottom: '16px',
              }}
            >
              researching
            </p>
            <h2
              style={{
                fontFamily: '"Cormorant Garamond", Georgia, serif',
                fontSize: '24px',
                fontWeight: 300,
                fontStyle: 'italic',
                color: colors.textLight,
                lineHeight: '1.4',
                maxWidth: '360px',
                margin: '0 auto',
              }}
            >
              "{input}"
            </h2>
          </div>

          {/* Progress indicator */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '48px',
              opacity: mounted ? 0.6 : 0,
              transition: 'opacity 0.8s ease-out 0.2s',
            }}
          >
            {agents.map((agent, i) => (
              <React.Fragment key={agent.name}>
                <div
                  style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor:
                      agent.status === 'complete'
                        ? colors.success
                        : agent.status === 'working'
                        ? colors.warning
                        : colors.border,
                    transition: 'all 0.4s ease',
                    animation: agent.status === 'working' ? 'breathe 2s ease-in-out infinite' : 'none',
                  }}
                />
                {i < agents.length - 1 && (
                  <div
                    style={{
                      width: '24px',
                      height: '1px',
                      backgroundColor: agent.status === 'complete' ? colors.success + '40' : colors.border,
                      transition: 'background-color 0.4s ease',
                    }}
                  />
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Agent cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {agents.map((agent, index) => {
              const nextAgent = agents[index + 1];
              const isFirstParallel = agent.name === 'Fact Checker' && nextAgent?.name === 'Content Editor';
              const isSecondParallel = agent.name === 'Content Editor' && agents[index - 1]?.name === 'Fact Checker';

              if (isSecondParallel) return null;

              if (isFirstParallel) {
                return (
                  <div
                    key="parallel-group"
                    style={{
                      opacity: mounted ? 1 : 0,
                      transform: mounted ? 'translateY(0)' : 'translateY(8px)',
                      transition: `all 0.6s ease-out ${0.3 + index * 0.1}s`,
                    }}
                  >
                    <p
                      style={{
                        fontFamily: '"Outfit", sans-serif',
                        fontSize: '10px',
                        letterSpacing: '0.15em',
                        textTransform: 'uppercase',
                        color: colors.textMuted,
                        textAlign: 'center',
                        marginBottom: '12px',
                        opacity: 0.5,
                      }}
                    >
                      parallel execution
                    </p>
                    <div style={{ display: 'flex', gap: '12px' }}>
                      {[agent, nextAgent].map((parallelAgent) => (
                        <AgentCard key={parallelAgent.name} agent={parallelAgent} compact />
                      ))}
                    </div>
                  </div>
                );
              }

              return (
                <div
                  key={agent.name}
                  style={{
                    opacity: mounted ? 1 : 0,
                    transform: mounted ? 'translateY(0)' : 'translateY(8px)',
                    transition: `all 0.6s ease-out ${0.3 + index * 0.1}s`,
                  }}
                >
                  <AgentCard agent={agent} />
                </div>
              );
            })}
          </div>

          {/* Finalizing message */}
          {allComplete && (
            <div
              style={{
                marginTop: '48px',
                textAlign: 'center',
                animation: 'fadeIn 0.8s ease-out',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '12px',
                }}
              >
                <div style={{ width: '20px', height: '1px', backgroundColor: colors.accent + '40' }} />
                <span
                  style={{
                    fontFamily: '"Cormorant Garamond", Georgia, serif',
                    fontSize: '14px',
                    fontStyle: 'italic',
                    color: colors.accent,
                    letterSpacing: '0.05em',
                    animation: 'breathe 2s ease-in-out infinite',
                  }}
                >
                  finalizing research...
                </span>
                <div style={{ width: '20px', height: '1px', backgroundColor: colors.accent + '40' }} />
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

function AgentCard({ agent, compact = false }: { agent: Agent; compact?: boolean }) {
  const isActive = agent.status === 'working';
  const isComplete = agent.status === 'complete';

  return (
    <div
      style={{
        flex: compact ? 1 : undefined,
        backgroundColor: colors.cardBg,
        border: `1px solid ${isComplete ? colors.success + '30' : isActive ? colors.warning + '30' : colors.border}`,
        borderRadius: '3px',
        padding: compact ? '14px 16px' : '18px 20px',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.4s ease',
      }}
    >
      {/* Shimmer effect for working state */}
      {isActive && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `linear-gradient(90deg, transparent, ${colors.warning}08, transparent)`,
            animation: 'shimmer 2s ease-in-out infinite',
          }}
        />
      )}

      <div style={{ position: 'relative', zIndex: 1 }}>
        {/* Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: agent.message && !compact ? '10px' : '0',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span
              style={{
                fontFamily: '"Outfit", sans-serif',
                fontSize: '14px',
                color: isComplete ? colors.success : isActive ? colors.warning : colors.textMuted,
                transition: 'color 0.3s ease',
                animation: isActive ? 'breathe 2s ease-in-out infinite' : 'none',
              }}
            >
              {getStatusIcon(agent.status)}
            </span>
            <span
              style={{
                fontFamily: '"Outfit", sans-serif',
                fontSize: compact ? '12px' : '13px',
                fontWeight: 400,
                color: isComplete || isActive ? colors.text : colors.textLight,
                letterSpacing: '0.01em',
                transition: 'color 0.3s ease',
              }}
            >
              {agent.name}
            </span>
          </div>

          {/* Status */}
          <span
            style={{
              fontFamily: '"Outfit", sans-serif',
              fontSize: '10px',
              letterSpacing: '0.1em',
              color: isComplete ? colors.success : isActive ? colors.warning : colors.textMuted,
              opacity: agent.status === 'waiting' ? 0.4 : 0.8,
              transition: 'all 0.3s ease',
            }}
          >
            {isComplete ? 'done' : isActive ? `${agent.progress}%` : ''}
          </span>
        </div>

        {/* Message */}
        {agent.message && !compact && (
          <p
            style={{
              fontFamily: '"Cormorant Garamond", Georgia, serif',
              fontSize: '13px',
              fontStyle: 'italic',
              color: colors.textLight,
              margin: 0,
              paddingLeft: '24px',
              opacity: 0.8,
            }}
          >
            {agent.message}
          </p>
        )}

        {/* Progress bar */}
        {(isActive || isComplete) && (
          <div
            style={{
              width: '100%',
              height: '1px',
              backgroundColor: colors.border,
              marginTop: compact ? '10px' : '14px',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                height: '100%',
                width: `${agent.progress}%`,
                backgroundColor: isComplete ? colors.success : colors.warning,
                transition: 'width 0.4s ease',
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
