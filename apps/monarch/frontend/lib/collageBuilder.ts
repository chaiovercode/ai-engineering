// LinkedIn carousel collage builder
import JSZip from "jszip";

export interface ChartSlideData {
  ticker: string;
  companyName: string | null;
  currentPrice: number;
  priceChangePercent: number;
  chartImage: string; // base64 PNG
}

export interface CarouselSlide {
  type: "hook" | "point" | "cta" | "chart";
  title?: string;
  content: string;
  slideNumber: number;
  totalSlides: number;
  chartData?: ChartSlideData;
}

export function parseContentToSlides(
  linkedInContent: string,
  hashtags: string[],
  chartData?: ChartSlideData
): CarouselSlide[] {
  const slides: CarouselSlide[] = [];
  const lines = linkedInContent.split("\n").filter((l) => l.trim());
  const hasChart = !!chartData;
  const totalSlides = hasChart ? 5 : 5; // Keep 5 slides either way

  // Slide 1: Hook/headline (first line or first sentence)
  const hookLine = lines[0] || "Key Market Insights";
  slides.push({
    type: "hook",
    content: hookLine,
    slideNumber: 1,
    totalSlides,
  });

  // Slide 2: Chart (if available) or first key point
  if (hasChart && chartData) {
    slides.push({
      type: "chart",
      content: `${chartData.ticker} Stock Performance`,
      slideNumber: 2,
      totalSlides,
      chartData,
    });
  }

  // Extract key points (look for bullet points, numbered items, or meaningful sentences)
  const keyPoints: string[] = [];
  for (const line of lines.slice(1)) {
    const trimmed = line.trim();
    // Skip short lines, hashtags, or emoji-only lines
    if (trimmed.length < 20 || trimmed.startsWith("#")) {
      continue;
    }
    // Remove bullet/number prefixes
    const cleaned = trimmed.replace(/^[\d.•\-\*]+\s*/, "");
    if (cleaned.length > 10 && keyPoints.length < (hasChart ? 2 : 3)) {
      keyPoints.push(cleaned);
    }
  }

  // Ensure we have enough key points
  const neededPoints = hasChart ? 2 : 3;
  while (keyPoints.length < neededPoints) {
    keyPoints.push(keyPoints[0] || "Market analysis insight");
  }

  // Key point slides
  const startSlideNum = hasChart ? 3 : 2;
  keyPoints.slice(0, neededPoints).forEach((point, i) => {
    slides.push({
      type: "point",
      title: `Key Point ${i + 1}`,
      content: point,
      slideNumber: startSlideNum + i,
      totalSlides,
    });
  });

  // CTA slide (always last)
  const ctaContent = hashtags.length > 0
    ? `Follow for more insights\n\n${hashtags.slice(0, 3).map((h) => `#${h}`).join(" ")}`
    : "Follow for more insights";

  slides.push({
    type: "cta",
    content: ctaContent,
    slideNumber: totalSlides,
    totalSlides,
  });

  return slides;
}

export async function downloadSlidesAsZip(
  slides: { blob: Blob; filename: string }[]
): Promise<void> {
  const zip = new JSZip();

  for (const slide of slides) {
    zip.file(slide.filename, slide.blob);
  }

  const content = await zip.generateAsync({ type: "blob" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(content);
  link.download = `monarch-carousel-${Date.now()}.zip`;
  link.click();
  URL.revokeObjectURL(link.href);
}
