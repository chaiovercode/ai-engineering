'use client';

import { useState, useEffect } from 'react';
import { colors } from '@/lib/colors';
import { streamResearch } from '@/lib/api';
import InputSection from '@/components/InputSection';
import AgentPipeline from '@/components/AgentPipeline';
import ResultsDisplay from '@/components/ResultsDisplay';
import ResearchSidebar from '@/components/ResearchSidebar';

interface AgentStatus {
  name: string;
  status: 'waiting' | 'working' | 'complete' | 'error';
  progress: number;
  message: string;
}

interface ResearchItem {
  id: string;
  input: string;
  type: 'topic' | 'url';
  content: string;
  timestamp: number;
}

export default function Home() {
  const [state, setState] = useState<'input' | 'generating' | 'results'>('input');
  const [agents, setAgents] = useState<AgentStatus[]>([
    { name: 'Content Strategist', status: 'waiting', progress: 0, message: '' },
    { name: 'Blog Writer', status: 'waiting', progress: 0, message: '' },
    { name: 'Content Editor', status: 'waiting', progress: 0, message: '' },
    { name: 'SEO Specialist', status: 'waiting', progress: 0, message: '' },
  ]);
  const [results, setResults] = useState<string>('');
  const [currentInput, setCurrentInput] = useState<{ input: string; type: 'topic' | 'url' }>({
    input: '',
    type: 'topic',
  });

  const handleSubmit = async (input: string, type: 'topic' | 'url', mode: 'gen-z' | 'analytical') => {
    setCurrentInput({ input, type });
    setState('generating');
    setAgents([
      { name: 'Content Strategist', status: 'waiting', progress: 0, message: '' },
      { name: 'Blog Writer', status: 'waiting', progress: 0, message: '' },
      { name: 'Content Editor', status: 'waiting', progress: 0, message: '' },
      { name: 'SEO Specialist', status: 'waiting', progress: 0, message: '' },
    ]);

    await streamResearch(input, type, mode, (event) => {
      console.log('Event received:', event.type, event.agent || '', event.progress || '');
      if (event.type === 'agent_start') {
        console.log('Agent starting:', event.agent);
        setAgents((prev) =>
          prev.map((a) =>
            a.name === event.agent
              ? { ...a, status: 'working', progress: 0, message: event.message || '' }
              : a
          )
        );
      } else if (event.type === 'agent_progress') {
        setAgents((prev) =>
          prev.map((a) =>
            a.name === event.agent
              ? {
                  ...a,
                  progress: event.progress || 0,
                  message: event.message || '',
                  status: (event.progress || 0) >= 100 ? 'complete' : 'working',
                }
              : a
          )
        );
      } else if (event.type === 'agent_complete') {
        setAgents((prev) =>
          prev.map((a) =>
            a.name === event.agent
              ? { ...a, status: 'complete', progress: 100 }
              : a
          )
        );
      } else if (event.type === 'complete') {
        console.log('Research complete');
        setResults(event.content || '');
        // Delay showing results so user can see final agent states
        setTimeout(() => {
          setState('results');
        }, 600);

        // Save to history
        if (typeof window !== 'undefined') {
          const newItem: ResearchItem = {
            id: Date.now().toString(),
            input,
            type,
            content: event.content || '',
            timestamp: Date.now(),
          };

          const existing = localStorage.getItem('researchHistory');
          const history = existing ? JSON.parse(existing) : [];
          const updated = [newItem, ...history];
          localStorage.setItem('researchHistory', JSON.stringify(updated));

          // Dispatch event to notify sidebar
          window.dispatchEvent(new Event('researchSaved'));
        }
      } else if (event.type === 'error') {
        setAgents((prev) =>
          prev.map((a) => ({ ...a, status: 'error' as const, message: event.message }))
        );
      }
    });
  };

  const handleShowHistory = (content: string) => {
    setResults(content);
    setState('results');
  };

  return (
    <div style={{ backgroundColor: colors.background, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <ResearchSidebar onSelectResearch={handleShowHistory} />

      <main style={{ paddingBottom: '0px', flex: 1 }}>
        {state === 'input' && <InputSection onSubmit={handleSubmit} />}
        {state === 'generating' && (
          <AgentPipeline agents={agents} input={currentInput.input} />
        )}
        {state === 'results' && (
          <ResultsDisplay
            content={results}
            onNewSearch={() => setState('input')}
          />
        )}
      </main>

      {/* Simple footer */}
      {state === 'input' && (
        <footer
          style={{
            textAlign: 'center',
            padding: '20px',
            fontSize: '11px',
            color: colors.textMuted,
            borderTop: `1px solid ${colors.border}`,
            height: '80px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <p style={{ margin: 0 }}>zensar research</p>
        </footer>
      )}
    </div>
  );
}
