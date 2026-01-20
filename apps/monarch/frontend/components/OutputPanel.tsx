"use client";

import type { TransformResponse } from "@/lib/api";
import type { StreamingState } from "@/app/page";
import { useState, useRef, forwardRef, useCallback } from "react";
import { fetchChartForTicker } from "@/lib/api";
import {
  CharacterLimitIndicator,
  CHARACTER_LIMITS,
} from "./CharacterLimitIndicator";
import { LinkedInPreview } from "./LinkedInPreview";
import { WhatsAppPreview } from "./WhatsAppPreview";
import { ExportButton } from "./ExportButton";
import { CollageGenerator } from "./CollageGenerator";
import { type StockChartData } from "./StockChart";
import { StockModal } from "./StockModal";
import { formatPrice, formatChange } from "@/utils/technicalIndicators";

interface OutputPanelProps {
  data: TransformResponse | null;
  isLoading: boolean;
  streaming?: StreamingState;
}

function CopyIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="9" y="9" width="13" height="13" rx="0" />
      <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
    </svg>
  );
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="brutal-button p-1.5 bg-white"
      title={copied ? "Copied!" : "Copy to clipboard"}
    >
      {copied ? (
        <CheckIcon className="w-4 h-4 text-[var(--gold)]" />
      ) : (
        <CopyIcon className="w-4 h-4" />
      )}
    </button>
  );
}

type ViewMode = "raw" | "preview";

// Vertical export poster for LinkedIn (1080x1350 - 4:5 ratio)
const LinkedInVerticalExport = forwardRef<HTMLDivElement, { content: string; hashtags: string[] }>(
  function LinkedInVerticalExport({ content, hashtags }, ref) {
    // Dynamic font sizing based on content length
    const getFontSize = (len: number): string => {
      if (len > 400) return "text-2xl";
      if (len > 300) return "text-3xl";
      if (len > 200) return "text-4xl";
      if (len > 100) return "text-5xl";
      return "text-5xl";
    };

    return (
      <div
        ref={ref}
        className="w-[1080px] h-[1350px] relative overflow-hidden"
        style={{ fontFamily: "'Outfit', system-ui, sans-serif" }}
      >
        <div className="w-full h-full bg-[#0f0f0f] flex flex-col relative">
          {/* Diagonal gold accent */}
          <div
            className="absolute top-0 right-0 w-[350px] h-[350px] bg-[#c9a227]"
            style={{ clipPath: "polygon(100% 0, 0 0, 100% 100%)" }}
          />

          {/* Bottom accent */}
          <div
            className="absolute bottom-0 left-0 w-full h-[120px] bg-[#c9a227]"
            style={{ clipPath: "polygon(0 60%, 100% 0, 100% 100%, 0 100%)" }}
          />

          {/* Content */}
          <div className="flex-1 flex flex-col px-16 py-14 relative z-10">
            {/* Logo */}
            <div className="mb-10">
              <img
                src="/mncl-logo.svg"
                alt="Monarch Networth Capital"
                className="h-14 w-auto"
              />
            </div>

            {/* Main content */}
            <div className="flex-1 flex flex-col justify-center">
              <p className={`${getFontSize(content.length)} font-bold text-white leading-[1.25]`}>
                {content}
              </p>

              {/* Hashtags */}
              {hashtags.length > 0 && (
                <div className="flex flex-wrap gap-3 mt-10">
                  {hashtags.slice(0, 5).map((tag) => (
                    <span
                      key={tag}
                      className="px-4 py-2 bg-[#1a1a1a] border border-[#333] text-[#c9a227] text-lg font-semibold"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="relative z-10 px-16 py-6 flex items-center justify-between">
            <p className="text-lg text-[#666] font-medium">mnclgroup.com</p>
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-[#00a651] to-[#008c44] rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <span className="text-lg text-white font-semibold">Monarch Networth Capital</span>
            </div>
          </div>
        </div>
      </div>
    );
  }
);


function ViewToggle({
  mode,
  onToggle,
}: {
  mode: ViewMode;
  onToggle: (mode: ViewMode) => void;
}) {
  return (
    <div className="flex items-center border-2 border-[var(--ink)] text-xs">
      <button
        onClick={() => onToggle("raw")}
        className={`px-2 py-1 font-medium transition-colors ${
          mode === "raw"
            ? "bg-[var(--ink)] text-[var(--paper)]"
            : "bg-white text-[var(--ink)] hover:bg-[var(--paper-dark)]"
        }`}
      >
        Raw
      </button>
      <button
        onClick={() => onToggle("preview")}
        className={`px-2 py-1 font-medium transition-colors ${
          mode === "preview"
            ? "bg-[var(--ink)] text-[var(--paper)]"
            : "bg-white text-[var(--ink)] hover:bg-[var(--paper-dark)]"
        }`}
      >
        Preview
      </button>
    </div>
  );
}

// Streaming cursor component
function StreamingCursor() {
  return (
    <span className="inline-block w-0.5 h-4 bg-[var(--gold)] ml-0.5 animate-blink align-middle" />
  );
}

interface LinkedInCardProps {
  data: TransformResponse["linkedin"] | null;
  streamingContent?: string;
  isStreaming?: boolean;
  chartData?: StockChartData | null;
}

function LinkedInCard({ data, streamingContent, isStreaming, chartData }: LinkedInCardProps) {
  const [viewMode, setViewMode] = useState<ViewMode>("raw");
  const previewRef = useRef<HTMLDivElement>(null);

  // Determine what content to display
  const displayContent = isStreaming ? streamingContent : data?.content;
  const displayHashtags = data?.hashtags || [];
  const hasContent = displayContent && displayContent.length > 0;

  if (!hasContent) {
    return (
      <div className="bg-white border-2 border-[var(--ink)] shadow-[4px_4px_0px_var(--ink)] h-full flex flex-col">
        <div className="px-4 py-3 border-b-2 border-[var(--ink)] bg-[var(--ink)]">
          <span className="text-sm font-bold uppercase tracking-wide text-[var(--paper)]">LinkedIn</span>
        </div>
        <div className="flex-1 p-6 flex items-center justify-center">
          <p className="text-[var(--slate)] text-sm">Generate to see LinkedIn post</p>
        </div>
      </div>
    );
  }

  const fullContent = displayHashtags.length > 0
    ? `${displayContent}\n\n${displayHashtags.map((h) => `#${h}`).join(" ")}`
    : displayContent || "";

  return (
    <div className="bg-white border-2 border-[var(--ink)] shadow-[4px_4px_0px_var(--ink)] h-full flex flex-col">
      <div className="px-4 py-3 border-b-2 border-[var(--ink)] bg-[var(--ink)] flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-sm font-bold uppercase tracking-wide text-[var(--paper)]">LinkedIn</span>
          {isStreaming && (
            <span className="text-xs text-[var(--gold)] animate-pulse font-medium">...</span>
          )}
        </div>
        <div className="flex items-center gap-1.5 flex-shrink-0">
          {!isStreaming && <ViewToggle mode={viewMode} onToggle={setViewMode} />}
          {!isStreaming && viewMode === "preview" && (
            <>
              <ExportButton targetRef={previewRef} filename="linkedin-post" />
              <CollageGenerator
                linkedInContent={displayContent || ""}
                hashtags={displayHashtags}
                chartData={chartData ? {
                  ticker: chartData.ticker,
                  companyName: chartData.company_name,
                  currentPrice: chartData.current_price,
                  priceChangePercent: chartData.price_change_percent,
                  chartImage: chartData.chart_image || "",
                } : undefined}
              />
            </>
          )}
          <CopyButton text={fullContent} />
        </div>
      </div>
      <div className="flex-1 p-5 overflow-auto flex flex-col">
        {viewMode === "raw" || isStreaming ? (
          <>
            <p className="text-sm leading-relaxed whitespace-pre-wrap mb-4 flex-1">
              {displayContent}
              {isStreaming && <StreamingCursor />}
            </p>
            {!isStreaming && displayHashtags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {displayHashtags.map((tag) => (
                  <span
                    key={tag}
                    className="text-xs bg-[var(--paper)] text-[var(--ink)] px-2 py-0.5 border border-[var(--ink)] font-medium"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="flex-1 mb-3">
            <LinkedInPreview content={displayContent || ""} hashtags={displayHashtags} />
            {/* Hidden vertical export version */}
            <div className="fixed -left-[9999px] top-0">
              <LinkedInVerticalExport ref={previewRef} content={displayContent || ""} hashtags={displayHashtags} />
            </div>
          </div>
        )}
        <CharacterLimitIndicator
          current={fullContent.length}
          limit={CHARACTER_LIMITS.linkedin}
        />
      </div>
    </div>
  );
}

interface WhatsAppCardProps {
  data: TransformResponse["whatsapp"] | null;
  streamingContent?: string;
  isStreaming?: boolean;
}

function WhatsAppCard({ data, streamingContent, isStreaming }: WhatsAppCardProps) {
  const [viewMode, setViewMode] = useState<ViewMode>("raw");
  const previewRef = useRef<HTMLDivElement>(null);

  // Determine what content to display
  const displayContent = isStreaming ? streamingContent : data?.formatted_message;
  const hasContent = displayContent && displayContent.length > 0;

  if (!hasContent) {
    return (
      <div className="bg-white border-2 border-[var(--ink)] shadow-[4px_4px_0px_var(--ink)] h-full flex flex-col">
        <div className="px-4 py-3 border-b-2 border-[var(--ink)] bg-[var(--ink)]">
          <span className="text-sm font-bold uppercase tracking-wide text-[var(--paper)]">WhatsApp</span>
        </div>
        <div className="flex-1 p-6 flex items-center justify-center">
          <p className="text-[var(--slate)] text-sm">Generate to see RM message</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border-2 border-[var(--ink)] shadow-[4px_4px_0px_var(--ink)] h-full flex flex-col">
      <div className="px-4 py-3 border-b-2 border-[var(--ink)] bg-[var(--ink)] flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-sm font-bold uppercase tracking-wide text-[var(--paper)]">WhatsApp</span>
          {isStreaming && (
            <span className="text-xs text-[var(--gold)] animate-pulse font-medium">...</span>
          )}
        </div>
        <div className="flex items-center gap-1.5 flex-shrink-0">
          {!isStreaming && <ViewToggle mode={viewMode} onToggle={setViewMode} />}
          {!isStreaming && viewMode === "preview" && (
            <ExportButton targetRef={previewRef} filename="whatsapp-message" />
          )}
          <CopyButton text={displayContent || ""} />
        </div>
      </div>
      <div className="flex-1 p-5 overflow-auto flex flex-col">
        {viewMode === "raw" || isStreaming ? (
          <div className="bg-[var(--paper)] border-2 border-[var(--ink)] p-4 flex-1">
            <div className="text-sm leading-relaxed">
              <span
                dangerouslySetInnerHTML={{
                  __html: (displayContent || "")
                    .replace(/\*([^*]+)\*/g, "<strong>$1</strong>")
                    .replace(/_([^_]+)_/g, "<em>$1</em>")
                    .replace(/\n/g, "<br />"),
                }}
              />
              {isStreaming && <StreamingCursor />}
            </div>
          </div>
        ) : (
          <div className="flex-1 mb-3">
            <WhatsAppPreview ref={previewRef} message={displayContent || ""} />
          </div>
        )}
        <CharacterLimitIndicator
          current={(displayContent || "").length}
          limit={CHARACTER_LIMITS.whatsapp}
          className="mt-3"
        />
      </div>
    </div>
  );
}

function SkeletonCard({ title }: { title: string }) {
  return (
    <div className="bg-white border-2 border-[var(--ink)] shadow-[4px_4px_0px_var(--ink)] h-full flex flex-col">
      <div className="px-4 py-3 border-b-2 border-[var(--ink)] bg-[var(--ink)]">
        <span className="text-sm font-bold uppercase tracking-wide text-[var(--paper)]">{title}</span>
      </div>
      <div className="flex-1 p-5 space-y-3">
        <div className="h-4 skeleton w-full" />
        <div className="h-4 skeleton w-5/6" />
        <div className="h-4 skeleton w-4/6" />
        <div className="h-4 skeleton w-3/4" />
        <div className="h-4 skeleton w-2/3" />
      </div>
    </div>
  );
}

interface TickerCardProps {
  data: StockChartData | null;
  isLoading?: boolean;
  loadingTicker?: string;
  onLoadTicker: (ticker: string) => void;
  onOpenChart: () => void;
}

// Ticker card with manual input
function TickerCard({ data, isLoading, loadingTicker, onLoadTicker, onOpenChart }: TickerCardProps) {
  const [inputTicker, setInputTicker] = useState("");
  const displayTicker = data?.ticker?.replace('.NS', '').replace('.BO', '') || '';
  const isPositive = (data?.price_change_percent || 0) >= 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputTicker.trim()) {
      onLoadTicker(inputTicker.trim().toUpperCase());
      setInputTicker("");
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="bg-[#0a0a0a] border-2 border-[var(--ink)] shadow-[4px_4px_0px_var(--ink)] p-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-[#1a1a1a] animate-pulse" />
          <div className="flex-1">
            <div className="h-5 w-24 bg-[#1a1a1a] animate-pulse mb-2" />
            <div className="h-3 w-32 bg-[#1a1a1a] animate-pulse" />
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">
              Loading <span className="text-[var(--gold)] font-semibold">{loadingTicker}</span>
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Has chart data - show ticker card
  if (data) {
    return (
      <div className="bg-[#0a0a0a] border-2 border-[var(--ink)] shadow-[4px_4px_0px_var(--ink)] p-4">
        <button
          onClick={onOpenChart}
          className="w-full text-left hover:opacity-90 transition-opacity"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-[var(--gold)] flex items-center justify-center flex-shrink-0">
              <span className="text-[#0a0a0a] font-black text-sm">
                {displayTicker.slice(0, 3)}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-black text-white">{displayTicker}</h3>
              {data.company_name && (
                <p className="text-xs text-gray-500 truncate">{data.company_name}</p>
              )}
            </div>
            <div className="text-right flex-shrink-0">
              <p className="text-xl font-black text-white">
                {formatPrice(data.current_price)}
              </p>
              <div className={`inline-flex items-center gap-1 ${
                isPositive ? 'text-green-400' : 'text-red-400'
              }`}>
                <span className="text-sm">{isPositive ? '▲' : '▼'}</span>
                <span className="text-sm font-bold">{formatChange(data.price_change_percent)}</span>
              </div>
            </div>
            <div className="flex-shrink-0 pl-2">
              <div className="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-[var(--gold)] transition-colors">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M7 17L17 7M17 7H7M17 7V17" />
                </svg>
              </div>
            </div>
          </div>
        </button>
        {/* Input to change ticker */}
        <form onSubmit={handleSubmit} className="mt-3 pt-3 border-t border-[#1a1a1a]">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputTicker}
              onChange={(e) => setInputTicker(e.target.value.toUpperCase())}
              placeholder="Change ticker (e.g., RELIANCE)"
              className="flex-1 bg-[#1a1a1a] border border-[#333] px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[var(--gold)]"
            />
            <button
              type="submit"
              disabled={!inputTicker.trim()}
              className="px-4 py-2 bg-[var(--gold)] text-[#0a0a0a] font-bold text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#d4ad2b] transition-colors"
            >
              Load
            </button>
          </div>
        </form>
      </div>
    );
  }

  // No data - show input to add ticker
  return (
    <div className="bg-[#0a0a0a] border-2 border-[var(--ink)] shadow-[4px_4px_0px_var(--ink)] p-4">
      <div className="flex items-center gap-4 mb-4">
        <div className="w-12 h-12 bg-[#1a1a1a] flex items-center justify-center">
          <svg className="w-6 h-6 text-[#444]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M3 3v18h18" />
            <path d="M7 12l4-4 4 4 5-5" />
          </svg>
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-400 font-medium">Add Stock Chart</p>
          <p className="text-xs text-gray-600">Enter NSE/BSE ticker symbol</p>
        </div>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="flex gap-2">
          <input
            type="text"
            value={inputTicker}
            onChange={(e) => setInputTicker(e.target.value.toUpperCase())}
            placeholder="Enter ticker (e.g., HAVELLS, TCS)"
            className="flex-1 bg-[#1a1a1a] border border-[#333] px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[var(--gold)]"
          />
          <button
            type="submit"
            disabled={!inputTicker.trim()}
            className="px-4 py-2 bg-[var(--gold)] text-[#0a0a0a] font-bold text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#d4ad2b] transition-colors"
          >
            Load
          </button>
        </div>
      </form>
    </div>
  );
}

export function OutputPanel({ data, isLoading, streaming }: OutputPanelProps) {
  const [isChartModalOpen, setIsChartModalOpen] = useState(false);
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [dynamicChartData, setDynamicChartData] = useState<StockChartData | null>(null);
  const [isLoadingChart, setIsLoadingChart] = useState(false);

  // Determine if we should show streaming content or final data
  const showLinkedInStreaming = !!(streaming?.isLinkedInStreaming || (streaming?.linkedInContent && !data?.linkedin?.content));
  const showWhatsAppStreaming = !!(streaming?.isWhatsAppStreaming || (streaming?.whatsAppContent && !data?.whatsapp?.formatted_message));

  // Show skeleton only if loading and no streaming content yet
  const showLinkedInSkeleton = isLoading && !streaming?.linkedInContent && !data?.linkedin;
  const showWhatsAppSkeleton = isLoading && !streaming?.whatsAppContent && !data?.whatsapp && !streaming?.isLinkedInStreaming;

  // Chart data from response (primary chart)
  const primaryChartData: StockChartData | null = data?.primary_chart
    ? {
        ticker: data.primary_chart.ticker,
        company_name: data.primary_chart.company_name,
        current_price: data.primary_chart.current_price,
        price_change_percent: data.primary_chart.price_change_percent,
        chart_image: data.primary_chart.chart_image,
        historical_prices: data.primary_chart.historical_prices,
      }
    : null;

  // Use dynamic chart data if user selected a different ticker, otherwise use primary
  const chartData = dynamicChartData || primaryChartData;

  // Handle loading a ticker - memoized for stable reference
  const handleLoadTicker = useCallback(async (ticker: string) => {
    setSelectedTicker(ticker);
    setIsLoadingChart(true);
    setDynamicChartData(null);

    try {
      const chart = await fetchChartForTicker(ticker);
      if (chart) {
        setDynamicChartData({
          ticker: chart.ticker,
          company_name: chart.company_name,
          current_price: chart.current_price,
          price_change_percent: chart.price_change_percent,
          chart_image: chart.chart_image,
          historical_prices: chart.historical_prices,
        });
      }
    } catch (error) {
      console.error("Failed to fetch chart:", error);
    } finally {
      setIsLoadingChart(false);
    }
  }, []);

  return (
    <div className="space-y-5">
      {/* Ticker Card - Manual input for stock symbol */}
      <TickerCard
          data={chartData}
          isLoading={isLoadingChart}
          loadingTicker={selectedTicker || undefined}
          onLoadTicker={handleLoadTicker}
          onOpenChart={() => setIsChartModalOpen(true)}
      />

      {/* Distribution outputs row: LinkedIn + WhatsApp */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {showLinkedInSkeleton ? (
          <SkeletonCard title="LinkedIn" />
        ) : (
          <LinkedInCard
            data={data?.linkedin || null}
            streamingContent={streaming?.linkedInContent}
            isStreaming={showLinkedInStreaming}
            chartData={chartData}
          />
        )}
        {showWhatsAppSkeleton ? (
          <SkeletonCard title="WhatsApp" />
        ) : (
          <WhatsAppCard
            data={data?.whatsapp || null}
            streamingContent={streaming?.whatsAppContent}
            isStreaming={showWhatsAppStreaming}
          />
        )}
      </div>

      {/* Stock Chart Modal */}
      {chartData && chartData.historical_prices && (
        <StockModal
          isOpen={isChartModalOpen}
          onClose={() => setIsChartModalOpen(false)}
          ticker={chartData.ticker}
          companyName={chartData.company_name}
          currentPrice={chartData.current_price}
          priceChangePercent={chartData.price_change_percent}
          historicalPrices={chartData.historical_prices}
        />
      )}
    </div>
  );
}
