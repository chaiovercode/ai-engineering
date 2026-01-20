"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { parseContentToSlides, downloadSlidesAsZip, type CarouselSlide, type ChartSlideData } from "@/lib/collageBuilder";
import { getImageBlob } from "@/lib/export";
import { formatPrice, formatChange } from "@/utils/technicalIndicators";

interface CollageGeneratorProps {
  linkedInContent: string;
  hashtags: string[];
  chartData?: ChartSlideData;
}

function GridIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="7" height="7" />
      <rect x="14" y="3" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" />
      <rect x="3" y="14" width="7" height="7" />
    </svg>
  );
}

// Dynamic font sizing based on content length
function getHookFontSize(content: string): string {
  const len = content.length;
  if (len > 150) return "text-3xl";
  if (len > 100) return "text-4xl";
  if (len > 60) return "text-5xl";
  return "text-6xl";
}

function getPointFontSize(content: string): string {
  const len = content.length;
  if (len > 200) return "text-xl";
  if (len > 150) return "text-2xl";
  if (len > 100) return "text-3xl";
  return "text-4xl";
}

// Individual slide renderer for capture
function CarouselSlideRender({ slide }: { slide: CarouselSlide }) {
  const pointNumber = slide.slideNumber - 1;

  return (
    <div
      className="w-[1080px] h-[1080px] relative overflow-hidden"
      style={{ fontFamily: "'Outfit', system-ui, sans-serif" }}
    >
      {/* ═══════════════════════════════════════════════════════════
          HOOK SLIDE - Bold dark design with gold accent
         ═══════════════════════════════════════════════════════════ */}
      {slide.type === "hook" && (
        <div className="w-full h-full bg-[#0f0f0f] flex flex-col relative">
          {/* Diagonal gold accent */}
          <div
            className="absolute top-0 right-0 w-[400px] h-[400px] bg-[#c9a227]"
            style={{ clipPath: "polygon(100% 0, 0 0, 100% 100%)" }}
          />

          {/* Content */}
          <div className="flex-1 flex flex-col justify-center px-20 py-16 relative z-10">
            {/* Logo */}
            <div className="mb-10">
              <img
                src="/mncl-logo.svg"
                alt="Monarch Networth Capital"
                className="h-14 w-auto"
              />
            </div>

            {/* Hook text */}
            <h1 className={`${getHookFontSize(slide.content)} font-black text-white leading-[1.1] max-w-[850px]`}>
              {slide.content}
            </h1>

            {/* Swipe indicator */}
            <div className="mt-auto pt-16 flex items-center gap-3">
              <span className="text-[#c9a227] text-lg font-semibold uppercase tracking-widest">Swipe</span>
              <div className="w-12 h-[2px] bg-[#c9a227]" />
              <span className="text-[#c9a227] text-2xl">→</span>
            </div>
          </div>

          {/* Footer */}
          <div className="px-20 py-6 flex items-center justify-between border-t border-[#333]">
            <p className="text-base text-[#666] font-medium">mnclgroup.com</p>
            <p className="text-base text-[#666]">{slide.slideNumber} / {slide.totalSlides}</p>
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════
          POINT SLIDES - Big number focus with content
         ═══════════════════════════════════════════════════════════ */}
      {slide.type === "point" && (
        <div className="w-full h-full bg-[#0f0f0f] flex flex-col relative">
          {/* Giant background number */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none select-none">
            <span
              className="text-[500px] font-black text-[#1a1a1a] leading-none"
              style={{ WebkitTextStroke: "2px #252525" }}
            >
              {pointNumber}
            </span>
          </div>

          {/* Gold accent bar */}
          <div className="absolute left-0 top-[200px] w-3 h-[300px] bg-[#c9a227]" />

          {/* Content */}
          <div className="flex-1 flex flex-col justify-center px-20 py-16 relative z-10">
            {/* Small number badge */}
            <div className="flex items-center gap-4 mb-8">
              <div className="w-16 h-16 bg-[#c9a227] flex items-center justify-center">
                <span className="text-3xl font-black text-[#0f0f0f]">{pointNumber}</span>
              </div>
              <div className="h-[2px] w-20 bg-[#c9a227]" />
            </div>

            {/* Point text */}
            <p className={`${getPointFontSize(slide.content)} font-bold text-white leading-[1.3] max-w-[800px]`}>
              {slide.content}
            </p>
          </div>

          {/* Footer */}
          <div className="px-20 py-6 flex items-center justify-between border-t border-[#333]">
            <p className="text-base text-[#666] font-medium">mnclgroup.com</p>
            <p className="text-base text-[#666]">{slide.slideNumber} / {slide.totalSlides}</p>
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════
          CHART SLIDE - Stock chart with price data
         ═══════════════════════════════════════════════════════════ */}
      {slide.type === "chart" && slide.chartData && (
        <div className="w-full h-full bg-[#0f0f0f] flex flex-col relative">
          {/* Gold accent bar */}
          <div className="absolute left-0 top-[150px] w-3 h-[200px] bg-[#c9a227]" />

          {/* Header with ticker info */}
          <div className="px-20 py-12 relative z-10">
            {/* Logo */}
            <div className="mb-6">
              <img
                src="/mncl-logo.svg"
                alt="Monarch Networth Capital"
                className="h-12 w-auto"
              />
            </div>

            {/* Ticker header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-5xl font-black text-white">
                  {slide.chartData.ticker.replace('.NS', '').replace('.BO', '')}
                </h1>
                {slide.chartData.companyName && (
                  <p className="text-xl text-[#666] mt-2">{slide.chartData.companyName}</p>
                )}
              </div>
              <div className="text-right">
                <p className="text-4xl font-bold text-white">
                  {formatPrice(slide.chartData.currentPrice)}
                </p>
                <p className={`text-2xl font-bold mt-1 ${
                  slide.chartData.priceChangePercent >= 0 ? 'text-[#00d395]' : 'text-[#ff4757]'
                }`}>
                  {slide.chartData.priceChangePercent >= 0 ? '▲' : '▼'} {formatChange(slide.chartData.priceChangePercent)}
                </p>
              </div>
            </div>
          </div>

          {/* Chart image */}
          <div className="flex-1 px-16 pb-8 flex items-center justify-center">
            <img
              src={`data:image/png;base64,${slide.chartData.chartImage}`}
              alt={`${slide.chartData.ticker} stock chart`}
              className="max-w-full max-h-full object-contain"
            />
          </div>

          {/* Footer */}
          <div className="px-20 py-6 flex items-center justify-between border-t border-[#333]">
            <p className="text-base text-[#666] font-medium">mnclgroup.com</p>
            <p className="text-base text-[#666]">{slide.slideNumber} / {slide.totalSlides}</p>
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════
          CTA SLIDE - Strong call to action
         ═══════════════════════════════════════════════════════════ */}
      {slide.type === "cta" && (
        <div className="w-full h-full bg-[#c9a227] flex flex-col relative">
          {/* Dark geometric shape */}
          <div
            className="absolute bottom-0 left-0 w-full h-[300px] bg-[#0f0f0f]"
            style={{ clipPath: "polygon(0 40%, 100% 0, 100% 100%, 0 100%)" }}
          />

          {/* Content */}
          <div className="flex-1 flex flex-col items-center justify-center px-20 py-16 relative z-10">
            {/* Logo */}
            <div className="mb-12">
              <img
                src="/mncl-logo.svg"
                alt="Monarch Networth Capital"
                className="h-16 w-auto"
              />
            </div>

            {/* CTA text */}
            <h2 className="text-6xl font-black text-[#0f0f0f] mb-6 text-center">
              Follow for more
            </h2>
            <h2 className="text-6xl font-black text-white mb-12 text-center">
              market insights
            </h2>

            {/* Hashtags */}
            <div className="flex flex-wrap justify-center gap-4">
              {slide.content.includes("#") &&
                slide.content
                  .split("\n")
                  .filter((l) => l.includes("#"))
                  .map((line) => (
                    <span
                      key={line}
                      className="px-6 py-3 bg-[#0f0f0f] text-[#c9a227] text-xl font-bold"
                    >
                      {line.trim()}
                    </span>
                  ))}
            </div>
          </div>

          {/* Footer */}
          <div className="relative z-10 px-20 py-6 flex items-center justify-between">
            <p className="text-base text-white font-medium">mnclgroup.com</p>
            <p className="text-base text-white">{slide.slideNumber} / {slide.totalSlides}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export function CollageGenerator({ linkedInContent, hashtags, chartData }: CollageGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewSlides, setPreviewSlides] = useState<CarouselSlide[] | null>(null);
  const slideRefs = useRef<(HTMLDivElement | null)[]>([]);
  const pendingExport = useRef(false);

  // Generate slides when content changes
  const generateSlides = useCallback(() => {
    const slides = parseContentToSlides(linkedInContent, hashtags, chartData);
    setPreviewSlides(slides);
    return slides;
  }, [linkedInContent, hashtags, chartData]);

  // Export after slides are rendered
  const doExport = useCallback(async () => {
    setIsGenerating(true);

    try {
      // Wait for DOM to render
      await new Promise((r) => setTimeout(r, 200));

      const slideBlobs: { blob: Blob; filename: string }[] = [];

      for (let i = 0; i < slideRefs.current.length; i++) {
        const ref = slideRefs.current[i];
        if (ref) {
          const blob = await getImageBlob(ref, { pixelRatio: 1 });
          slideBlobs.push({
            blob,
            filename: `slide-${i + 1}.png`,
          });
        }
      }

      if (slideBlobs.length > 0) {
        await downloadSlidesAsZip(slideBlobs);
      }
    } catch (error) {
      console.error("Failed to generate carousel:", error);
    } finally {
      setIsGenerating(false);
      pendingExport.current = false;
    }
  }, []);

  // Handle click - generate slides then export
  const handleExport = async () => {
    if (isGenerating) return;

    // If we already have slides, just export
    if (previewSlides && previewSlides.length > 0) {
      await doExport();
      return;
    }

    // Otherwise generate slides first, then export
    pendingExport.current = true;
    generateSlides();
  };

  // When slides are generated and we have a pending export, do the export
  useEffect(() => {
    if (previewSlides && pendingExport.current) {
      doExport();
    }
  }, [previewSlides, doExport]);

  return (
    <div className="relative">
      <button
        onClick={handleExport}
        disabled={isGenerating}
        className="brutal-button p-1.5 bg-[var(--gold)] text-[var(--ink)] disabled:opacity-50"
        title={isGenerating ? "Generating carousel..." : "Export as carousel slides"}
      >
        {isGenerating ? (
          <span className="w-4 h-4 border-2 border-[var(--ink)] border-t-transparent rounded-full animate-spin" />
        ) : (
          <GridIcon className="w-4 h-4" />
        )}
      </button>

      {/* Hidden render area for slides */}
      {previewSlides && (
        <div className="fixed -left-[9999px] top-0">
          {previewSlides.map((slide, i) => (
            <div
              key={i}
              ref={(el) => {
                slideRefs.current[i] = el;
              }}
            >
              <CarouselSlideRender slide={slide} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
