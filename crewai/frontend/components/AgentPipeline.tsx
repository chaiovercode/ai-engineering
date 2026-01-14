'use client';

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

const agentIcons: Record<string, string> = {
  'Content Strategist': '•',
  'Blog Writer': '•',
  'Content Editor': '•',
  'SEO Specialist': '•',
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
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        padding: '40px 20px',
        backgroundColor: colors.background,
      }}
    >
      <div style={{ width: '100%', maxWidth: '600px' }}>
        {/* Header */}
        <div style={{ marginBottom: '40px', textAlign: 'center' }}>
          <h2
            style={{
              fontSize: '18px',
              fontWeight: 400,
              color: colors.text,
              marginBottom: '8px',
            }}
          >
            researching...
          </h2>
          <p
            style={{
              fontSize: '12px',
              color: colors.textLight,
            }}
          >
            {input}
          </p>
        </div>

        {/* Agents */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {agents.map((agent) => (
            <div
              key={agent.name}
              style={{
                backgroundColor: colors.cardBg,
                border: `1px solid ${colors.border}`,
                borderRadius: '8px',
                padding: '16px',
                transition: 'all 200ms ease',
              }}
            >
              {/* Agent header */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '8px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '8px',
                    flex: 1,
                  }}
                >
                  <span style={{ fontSize: '14px', color: colors.text, marginTop: '2px' }}>
                    {agentIcons[agent.name] || '•'}
                  </span>
                  <div style={{ flex: 1 }}>
                    <span
                      style={{
                        fontSize: '13px',
                        fontWeight: 400,
                        color: colors.text,
                      }}
                    >
                      {agent.name}
                    </span>
                    {agent.message && (
                      <p
                        style={{
                          fontSize: '12px',
                          color: colors.textLight,
                          marginTop: '4px',
                          marginBottom: '0px',
                          lineHeight: '1.4',
                        }}
                      >
                        {agent.message}
                      </p>
                    )}
                  </div>
                </div>
                <span
                  style={{
                    fontSize: '10px',
                    color: getStatusColor(agent.status),
                    fontWeight: 400,
                    marginTop: '2px',
                    marginLeft: '8px',
                  }}
                >
                  {agent.status === 'complete' && 'done'}
                  {agent.status === 'working' && 'processing'}
                  {agent.status === 'waiting' && 'waiting'}
                  {agent.status === 'error' && 'error'}
                </span>
              </div>

              {/* Progress bar */}
              {agent.status !== 'waiting' && (
                <div
                  style={{
                    width: '100%',
                    height: '4px',
                    backgroundColor: colors.surface,
                    borderRadius: '2px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      width: `${agent.progress}%`,
                      backgroundColor: getStatusColor(agent.status),
                      borderRadius: '2px',
                      transition: 'width 300ms ease',
                    }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
