'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { colors } from '@/lib/colors';
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
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    // Load research from API
    const loadResearch = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8008/api/research/${id}`);
        if (!response.ok) {
          throw new Error('Research not found');
        }
        const data = await response.json();
        // Check if response has error field (shouldn't happen now with proper 404)
        if (data.error) {
          throw new Error(data.error);
        }
        setResearch(data);
        setLoading(false);
      } catch (err) {
        console.error('Failed to load research:', err);
        setLoading(false);
        setNotFound(true);
        // Research not found, redirect to home after brief delay
        setTimeout(() => {
          router.push('/');
        }, 1500);
      }
    };

    if (id) {
      loadResearch();
    }
  }, [id, router]);

  const handleShowHistory = (_content: string) => {
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
        ) : notFound ? (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100vh',
              fontSize: '14px',
              color: colors.textMuted,
              gap: '12px',
            }}
          >
            <span>research not found</span>
            <span style={{ fontSize: '12px' }}>redirecting to home...</span>
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
                    marginBottom: '32px',
                    textAlign: 'center',
                  }}
                >
                  <h2
                    style={{
                      fontSize: '18px',
                      fontWeight: 400,
                      color: colors.text,
                    }}
                  >
                    {research.input}
                  </h2>
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
