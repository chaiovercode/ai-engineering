'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { colors } from '@/lib/colors';
import { fetchHistory } from '@/lib/api';
import ResultsDisplay from '@/components/ResultsDisplay';
import ResearchSidebar from '@/components/ResearchSidebar';

interface ResearchItem {
  id: string;
  input: string;
  type: 'topic' | 'url';
  content: string;
  timestamp: number;
}

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [research, setResearch] = useState<ResearchItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load research from API
    const loadResearch = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8008/api/research/${id}`);
        if (!response.ok) {
          throw new Error('Research not found');
        }
        const data = await response.json();
        setResearch(data);
        setLoading(false);
      } catch (err) {
        console.error('Failed to load research:', err);
        // Research not found, redirect to home
        setTimeout(() => {
          router.push('/');
        }, 300);
      }
    };

    if (id) {
      loadResearch();
    }
  }, [id, router]);

  const handleShowHistory = (content: string) => {
    // This is called when user clicks on a research item from sidebar
    // The sidebar will navigate directly, so we don't need to do anything here
    // The useEffect above will fetch the new research based on the URL param
  };

  return (
    <div style={{ backgroundColor: colors.background, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <ResearchSidebar onSelectResearch={handleShowHistory} />

      <main style={{ paddingBottom: '0px', flex: 1 }}>
        {loading ? (
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100vh',
              fontSize: '14px',
              color: colors.textLight,
            }}
          >
            loading...
          </div>
        ) : research ? (
          <>
            <div
              style={{
                padding: '20px 20px 40px 20px',
                display: 'flex',
                justifyContent: 'center',
              }}
            >
              <div style={{ width: '100%', maxWidth: '900px' }}>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '32px',
                  }}
                >
                  <h2
                    style={{
                      fontSize: '18px',
                      fontWeight: 400,
                      color: colors.text,
                      marginLeft: '30px',
                    }}
                  >
                    {research.input}
                  </h2>
                  <button
                    onClick={() => router.push('/')}
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
                      marginRight: '30px',
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

                <ResultsDisplay
                  content={research.content}
                  onNewSearch={() => router.push('/')}
                />
              </div>
            </div>
          </>
        ) : null}
      </main>
    </div>
  );
}
