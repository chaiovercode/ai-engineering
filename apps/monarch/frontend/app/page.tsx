"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import Image from "next/image";
import { InputPanel } from "@/components/InputPanel";
import { OutputPanel } from "@/components/OutputPanel";
import { ReportSidebar } from "@/components/ReportSidebar";
import { KeyboardHints } from "@/components/KeyboardHints";
import { transformReportStream, TransformResponse, Tone, Variant, StockChartOutput } from "@/lib/api";
import { useReportHistory } from "@/hooks/useReportHistory";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { triggerCelebration } from "@/lib/confetti";
import type { SavedReport } from "@/lib/storage";

export interface StreamingState {
  isLinkedInStreaming: boolean;
  isWhatsAppStreaming: boolean;
  linkedInContent: string;
  whatsAppContent: string;
  isChartLoading: boolean;
  chartLoadingTicker: string;
}

export interface VariantData {
  linkedin: TransformResponse["linkedin"] | null;
  whatsapp: TransformResponse["whatsapp"] | null;
  detectedTickers: string[];
  primaryChart: StockChartOutput | null;
}

export default function Home() {
  const [reportText, setReportText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tone, setTone] = useState<Tone>("professional");
  const [mounted, setMounted] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeReportId, setActiveReportId] = useState<string | null>(null);

  // Variant states
  const [activeVariant, setActiveVariant] = useState<Variant>("A");
  const [variantA, setVariantA] = useState<VariantData>({ linkedin: null, whatsapp: null, detectedTickers: [], primaryChart: null });
  const [variantB, setVariantB] = useState<VariantData>({ linkedin: null, whatsapp: null, detectedTickers: [], primaryChart: null });
  const [isGeneratingVariantB, setIsGeneratingVariantB] = useState(false);

  // Streaming state
  const [streaming, setStreaming] = useState<StreamingState>({
    isLinkedInStreaming: false,
    isWhatsAppStreaming: false,
    linkedInContent: "",
    whatsAppContent: "",
    isChartLoading: false,
    chartLoadingTicker: "",
  });

  // Report history
  const {
    reports,
    saveCurrentReport,
    removeReport,
    updateReportTitle,
    updateReportVariantB,
  } = useReportHistory();

  // Track if we should auto-save on completion
  const pendingSave = useRef<{ variant: Variant; reportText: string; tone: string } | null>(null);
  // Track if we need to update existing report with Version B
  const pendingVariantBUpdate = useRef<string | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  const generateVariant = useCallback(
    async (variant: Variant) => {
      if (!reportText.trim()) return;

      const isVariantB = variant === "B";
      if (isVariantB) {
        setIsGeneratingVariantB(true);
        setActiveVariant("B");
      } else {
        setIsLoading(true);
        setVariantA({ linkedin: null, whatsapp: null, detectedTickers: [], primaryChart: null });
        setVariantB({ linkedin: null, whatsapp: null, detectedTickers: [], primaryChart: null });
        setActiveReportId(null);
      }

      setError(null);

      setStreaming({
        isLinkedInStreaming: false,
        isWhatsAppStreaming: false,
        linkedInContent: "",
        whatsAppContent: "",
        isChartLoading: false,
        chartLoadingTicker: "",
      });

      const setVariantData = isVariantB ? setVariantB : setVariantA;

      // Track for auto-save - only for Version A (new report)
      // Version B updates an existing report, handled separately
      if (!isVariantB) {
        pendingSave.current = { variant, reportText, tone };
      } else if (activeReportId) {
        // Track that we need to update existing report with Version B
        pendingVariantBUpdate.current = activeReportId;
      }

      try {
        await transformReportStream(
          reportText,
          {
            onLinkedInStart: () => {
              setStreaming((prev) => ({
                ...prev,
                isLinkedInStreaming: true,
                linkedInContent: "",
              }));
            },
            onLinkedInChunk: (chunk) => {
              setStreaming((prev) => ({
                ...prev,
                linkedInContent: prev.linkedInContent + chunk,
              }));
            },
            onLinkedInComplete: (content, hashtags, charCount) => {
              setStreaming((prev) => ({
                ...prev,
                isLinkedInStreaming: false,
              }));
              setVariantData((prev) => ({
                ...prev,
                linkedin: {
                  content,
                  hashtags,
                  character_count: charCount,
                },
              }));
            },
            onWhatsAppStart: () => {
              setStreaming((prev) => ({
                ...prev,
                isWhatsAppStreaming: true,
                whatsAppContent: "",
              }));
            },
            onWhatsAppChunk: (chunk) => {
              setStreaming((prev) => ({
                ...prev,
                whatsAppContent: prev.whatsAppContent + chunk,
              }));
            },
            onWhatsAppComplete: (content) => {
              setStreaming((prev) => ({
                ...prev,
                isWhatsAppStreaming: false,
              }));
              setVariantData((prev) => ({
                ...prev,
                whatsapp: {
                  formatted_message: content,
                  plain_text: content.replace(/\*|_/g, ""),
                },
              }));
            },
            onTickersDetected: (tickers) => {
              setVariantData((prev) => ({
                ...prev,
                detectedTickers: tickers,
              }));
            },
            onChartStart: (ticker) => {
              setStreaming((prev) => ({
                ...prev,
                isChartLoading: true,
                chartLoadingTicker: ticker,
              }));
            },
            onChartComplete: (chart) => {
              setStreaming((prev) => ({
                ...prev,
                isChartLoading: false,
                chartLoadingTicker: "",
              }));
              setVariantData((prev) => ({
                ...prev,
                primaryChart: chart,
              }));
            },
            onChartError: () => {
              setStreaming((prev) => ({
                ...prev,
                isChartLoading: false,
                chartLoadingTicker: "",
              }));
            },
            onDone: () => {
              if (isVariantB) {
                setIsGeneratingVariantB(false);
              } else {
                setIsLoading(false);
              }
              // Trigger celebration
              triggerCelebration();
            },
            onError: (err) => {
              const errorMessage = typeof err.message === 'string' ? err.message : String(err);
              setError(errorMessage);
              pendingSave.current = null;
              if (isVariantB) {
                setIsGeneratingVariantB(false);
              } else {
                setIsLoading(false);
              }
            },
          },
          tone,
          variant
        );
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : (typeof err === 'string' ? err : "An error occurred");
        setError(errorMessage);
        pendingSave.current = null;
        if (isVariantB) {
          setIsGeneratingVariantB(false);
        } else {
          setIsLoading(false);
        }
      }
    },
    [reportText, tone]
  );

  // Auto-save after generation completes
  useEffect(() => {
    if (
      pendingSave.current &&
      !isLoading &&
      !isGeneratingVariantB &&
      variantA.linkedin
    ) {
      const { reportText: savedReportText, tone: savedTone } = pendingSave.current;
      const saved = saveCurrentReport({
        reportText: savedReportText,
        tone: savedTone,
        linkedin: variantA.linkedin,
        whatsapp: variantA.whatsapp,
        detectedTickers: variantA.detectedTickers,
        primaryChart: variantA.primaryChart ? {
          ticker: variantA.primaryChart.ticker,
          company_name: variantA.primaryChart.company_name,
          current_price: variantA.primaryChart.current_price,
          price_change_percent: variantA.primaryChart.price_change_percent,
          chart_image: variantA.primaryChart.chart_image,
        } : null,
        variantB: variantB.linkedin
          ? {
              linkedin: variantB.linkedin,
              whatsapp: variantB.whatsapp,
              detectedTickers: variantB.detectedTickers,
              primaryChart: variantB.primaryChart ? {
                ticker: variantB.primaryChart.ticker,
                company_name: variantB.primaryChart.company_name,
                current_price: variantB.primaryChart.current_price,
                price_change_percent: variantB.primaryChart.price_change_percent,
                chart_image: variantB.primaryChart.chart_image,
              } : null,
            }
          : undefined,
      });
      setActiveReportId(saved.id);
      pendingSave.current = null;
    }
  }, [isLoading, isGeneratingVariantB, variantA, variantB, saveCurrentReport]);

  // Update existing report with Version B data when generation completes
  useEffect(() => {
    if (
      pendingVariantBUpdate.current &&
      !isGeneratingVariantB &&
      variantB.linkedin
    ) {
      updateReportVariantB(pendingVariantBUpdate.current, {
        linkedin: variantB.linkedin,
        whatsapp: variantB.whatsapp,
        detectedTickers: variantB.detectedTickers,
        primaryChart: variantB.primaryChart ? {
          ticker: variantB.primaryChart.ticker,
          company_name: variantB.primaryChart.company_name,
          current_price: variantB.primaryChart.current_price,
          price_change_percent: variantB.primaryChart.price_change_percent,
          chart_image: variantB.primaryChart.chart_image,
        } : null,
      });
      pendingVariantBUpdate.current = null;
    }
  }, [isGeneratingVariantB, variantB, updateReportVariantB]);

  const handleGenerate = useCallback(() => {
    setActiveVariant("A");
    generateVariant("A");
  }, [generateVariant]);

  const handleGenerateVariantB = useCallback(() => {
    generateVariant("B");
  }, [generateVariant]);

  const handleSelectReport = useCallback((report: SavedReport) => {
    setReportText(report.reportText);
    setTone(report.tone as Tone);
    setVariantA({
      linkedin: report.linkedin,
      whatsapp: report.whatsapp,
      detectedTickers: report.detectedTickers || [],
      primaryChart: report.primaryChart || null,
    });
    setVariantB({
      linkedin: report.variantB?.linkedin || null,
      whatsapp: report.variantB?.whatsapp || null,
      detectedTickers: report.variantB?.detectedTickers || [],
      primaryChart: report.variantB?.primaryChart || null,
    });
    setActiveVariant("A");
    setActiveReportId(report.id);
    setSidebarOpen(false);
  }, []);

  const handleManualSave = useCallback(() => {
    if (variantA.linkedin) {
      const saved = saveCurrentReport({
        reportText,
        tone,
        linkedin: variantA.linkedin,
        whatsapp: variantA.whatsapp,
        detectedTickers: variantA.detectedTickers,
        primaryChart: variantA.primaryChart ? {
          ticker: variantA.primaryChart.ticker,
          company_name: variantA.primaryChart.company_name,
          current_price: variantA.primaryChart.current_price,
          price_change_percent: variantA.primaryChart.price_change_percent,
          chart_image: variantA.primaryChart.chart_image,
        } : null,
        variantB: variantB.linkedin
          ? {
              linkedin: variantB.linkedin,
              whatsapp: variantB.whatsapp,
              detectedTickers: variantB.detectedTickers,
              primaryChart: variantB.primaryChart ? {
                ticker: variantB.primaryChart.ticker,
                company_name: variantB.primaryChart.company_name,
                current_price: variantB.primaryChart.current_price,
                price_change_percent: variantB.primaryChart.price_change_percent,
                chart_image: variantB.primaryChart.chart_image,
              } : null,
            }
          : undefined,
      });
      setActiveReportId(saved.id);
    }
  }, [reportText, tone, variantA, variantB, saveCurrentReport]);

  const handleNewReport = useCallback(() => {
    setReportText("");
    setTone("professional");
    setVariantA({ linkedin: null, whatsapp: null, detectedTickers: [], primaryChart: null });
    setVariantB({ linkedin: null, whatsapp: null, detectedTickers: [], primaryChart: null });
    setActiveVariant("A");
    setActiveReportId(null);
    setError(null);
    setStreaming({
      isLinkedInStreaming: false,
      isWhatsAppStreaming: false,
      linkedInContent: "",
      whatsAppContent: "",
      isChartLoading: false,
      chartLoadingTicker: "",
    });
  }, []);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onGenerate: handleGenerate,
    onGenerateB: variantA.linkedin && !isLoading && !isGeneratingVariantB ? handleGenerateVariantB : undefined,
    onSwitchToA: () => setActiveVariant("A"),
    onSwitchToB: variantB.linkedin ? () => setActiveVariant("B") : undefined,
    onSave: handleManualSave,
    onToggleSidebar: () => setSidebarOpen((prev) => !prev),
  });

  const currentVariant = activeVariant === "A" ? variantA : variantB;
  // Show result when we have content OR detected tickers (tickers arrive first during streaming)
  const hasData = currentVariant.linkedin || currentVariant.whatsapp || currentVariant.detectedTickers.length > 0;
  const result: TransformResponse | null = hasData
    ? {
        linkedin: currentVariant.linkedin || {
          content: "",
          hashtags: [],
          character_count: 0,
        },
        newsletter: {
          headline: "",
          thesis: "",
          key_points: [],
          call_to_action: "",
        },
        whatsapp: currentVariant.whatsapp || {
          formatted_message: "",
          plain_text: "",
        },
        detected_tickers: currentVariant.detectedTickers,
        primary_chart: currentVariant.primaryChart || undefined,
      }
    : null;

  const canGenerateVariantB = variantA.linkedin !== null && !isLoading && !isGeneratingVariantB;
  const showVariantTabs = variantA.linkedin !== null;

  if (!mounted) return null;

  return (
    <div className="h-screen flex flex-col bg-[var(--paper)] overflow-hidden">
      {/* Header - full width */}
      <header className="flex-shrink-0 bg-white border-b-2 border-[var(--ink)] z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image
              src="/mncl-logo.svg"
              alt="Monarch Networth Capital"
              width={170}
              height={40}
              className="h-10 w-auto"
              priority
            />
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleNewReport}
              className="brutal-button px-4 py-2 bg-white text-[var(--ink)] text-sm font-bold flex items-center gap-2 hover:bg-[var(--paper-dark)]"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 5v14M5 12h14" />
              </svg>
              New
            </button>
            <div className="brutal-card px-4 py-2">
              <span className="text-sm font-semibold text-[var(--ink)]">Report Transformer</span>
              <span className="ml-2 text-xs px-2 py-0.5 bg-[var(--gold)] text-[var(--ink)] font-semibold">
                AI
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Body - sidebar + content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Report History Sidebar */}
        <ReportSidebar
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          reports={reports}
          activeReportId={activeReportId}
          onSelectReport={handleSelectReport}
          onDeleteReport={removeReport}
          onUpdateTitle={updateReportTitle}
        />

        {/* Main content area */}
        <main className="flex-1 min-w-0 overflow-auto">
          <div className="px-6 py-8">
            {/* Error message */}
            {error && (
              <div className="mb-6 p-4 brutal-card border-red-500 bg-red-50 text-red-700 text-sm">
                {error}
              </div>
            )}

            {/* Variant Tabs */}
            {showVariantTabs && (
              <div className="mb-6 flex items-center gap-4">
                <div className="flex border-2 border-[var(--ink)]">
                  <button
                    onClick={() => setActiveVariant("A")}
                    className={`px-4 py-2 text-sm font-bold transition-colors ${
                      activeVariant === "A"
                        ? "bg-[var(--gold)] text-[var(--ink)]"
                        : "bg-white text-[var(--ink)] hover:bg-[var(--paper-dark)]"
                    }`}
                  >
                    Version A
                  </button>
                  <button
                    onClick={() => setActiveVariant("B")}
                    disabled={!variantB.linkedin && !isGeneratingVariantB}
                    className={`px-4 py-2 text-sm font-bold transition-colors border-l-2 border-[var(--ink)] ${
                      activeVariant === "B"
                        ? "bg-[var(--ink)] text-[var(--paper)]"
                        : "bg-white text-[var(--ink)] hover:bg-[var(--paper-dark)]"
                    } ${!variantB.linkedin && !isGeneratingVariantB ? "opacity-40 cursor-not-allowed" : ""}`}
                  >
                    Version B
                  </button>
                </div>

                {canGenerateVariantB && !variantB.linkedin && (
                  <button
                    onClick={handleGenerateVariantB}
                    className="brutal-button px-4 py-2 text-sm font-bold text-[var(--ink)] bg-white"
                  >
                    + Generate Alternative
                  </button>
                )}

                {isGeneratingVariantB && (
                  <span className="text-sm text-[var(--gold)] font-medium animate-pulse">
                    Generating Version B...
                  </span>
                )}
              </div>
            )}

            {/* Main content grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Input panel */}
              <div className="lg:col-span-4">
                <InputPanel
                  value={reportText}
                  onChange={setReportText}
                  onGenerate={handleGenerate}
                  isLoading={isLoading || isGeneratingVariantB}
                  tone={tone}
                  onToneChange={setTone}
                />
              </div>

              {/* Output panel */}
              <div className="lg:col-span-8">
                <OutputPanel
                  data={result}
                  isLoading={isLoading || (isGeneratingVariantB && activeVariant === "B")}
                  streaming={
                    (activeVariant === "A" && !variantA.linkedin) ||
                    (activeVariant === "B" && !variantB.linkedin && isGeneratingVariantB)
                      ? streaming
                      : undefined
                  }
                />
              </div>
            </div>

            {/* Footer */}
            <footer className="mt-12 pt-6 border-t-2 border-gray-200 text-center">
              <p className="text-xs text-gray-500">
                Powered by AI • Monarch Networth Capital © {new Date().getFullYear()}
              </p>
            </footer>
          </div>
        </main>
      </div>

      {/* Keyboard Hints */}
      <KeyboardHints />
    </div>
  );
}
