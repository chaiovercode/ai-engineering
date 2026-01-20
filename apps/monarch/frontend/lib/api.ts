const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface LinkedInOutput {
  content: string;
  hashtags: string[];
  character_count: number;
}

export interface NewsletterOutput {
  headline: string;
  thesis: string;
  key_points: string[];
  call_to_action: string;
}

export interface WhatsAppOutput {
  formatted_message: string;
  plain_text: string;
}

export interface HistoricalPrice {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface StockChartOutput {
  ticker: string;
  company_name: string | null;
  current_price: number;
  price_change_percent: number;
  chart_image: string;
  historical_prices?: HistoricalPrice[];
}

export interface TransformResponse {
  linkedin: LinkedInOutput;
  newsletter: NewsletterOutput;
  whatsapp: WhatsAppOutput;
  detected_tickers?: string[];
  primary_chart?: StockChartOutput;
}

export type Tone = "professional" | "conversational" | "punchy";
export type Variant = "A" | "B";

export interface TransformRequest {
  report_text: string;
  tone?: Tone;
  variant?: Variant;
}

export async function transformReport(
  reportText: string
): Promise<TransformResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/transform`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ report_text: reportText }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to transform report");
  }

  return response.json();
}

// Streaming types
export interface StreamEvent {
  type:
    | "linkedin_start"
    | "linkedin_chunk"
    | "linkedin_complete"
    | "whatsapp_start"
    | "whatsapp_chunk"
    | "whatsapp_complete"
    | "tickers_detected"
    | "chart_start"
    | "chart_complete"
    | "chart_error"
    | "done";
  content?: string;
  hashtags?: string[];
  character_count?: number;
  tickers?: string[];
  ticker?: string;
  chart?: StockChartOutput;
  error?: string;
}

export interface StreamCallbacks {
  onLinkedInStart?: () => void;
  onLinkedInChunk?: (chunk: string) => void;
  onLinkedInComplete?: (content: string, hashtags: string[], charCount: number) => void;
  onWhatsAppStart?: () => void;
  onWhatsAppChunk?: (chunk: string) => void;
  onWhatsAppComplete?: (content: string) => void;
  onTickersDetected?: (tickers: string[]) => void;
  onChartStart?: (ticker: string) => void;
  onChartComplete?: (chart: StockChartOutput) => void;
  onChartError?: (error: string) => void;
  onDone?: () => void;
  onError?: (error: Error) => void;
}

export async function transformReportStream(
  reportText: string,
  callbacks: StreamCallbacks,
  tone: Tone = "professional",
  variant: Variant = "A"
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/transform/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ report_text: reportText, tone, variant }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to transform report");
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE events
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || ""; // Keep incomplete event in buffer

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const jsonStr = line.slice(6);
          try {
            const event: StreamEvent = JSON.parse(jsonStr);

            switch (event.type) {
              case "linkedin_start":
                callbacks.onLinkedInStart?.();
                break;
              case "linkedin_chunk":
                callbacks.onLinkedInChunk?.(typeof event.content === 'string' ? event.content : "");
                break;
              case "linkedin_complete":
                callbacks.onLinkedInComplete?.(
                  typeof event.content === 'string' ? event.content : "",
                  Array.isArray(event.hashtags) ? event.hashtags : [],
                  typeof event.character_count === 'number' ? event.character_count : 0
                );
                break;
              case "whatsapp_start":
                callbacks.onWhatsAppStart?.();
                break;
              case "whatsapp_chunk":
                callbacks.onWhatsAppChunk?.(typeof event.content === 'string' ? event.content : "");
                break;
              case "whatsapp_complete":
                callbacks.onWhatsAppComplete?.(typeof event.content === 'string' ? event.content : "");
                break;
              case "tickers_detected":
                callbacks.onTickersDetected?.(event.tickers || []);
                break;
              case "chart_start":
                callbacks.onChartStart?.(event.ticker || "");
                break;
              case "chart_complete":
                if (event.chart) {
                  callbacks.onChartComplete?.(event.chart);
                }
                break;
              case "chart_error":
                callbacks.onChartError?.(event.error || "Unknown error");
                break;
              case "done":
                callbacks.onDone?.();
                break;
            }
          } catch (e) {
            console.error("Failed to parse SSE event:", e);
          }
        }
      }
    }
  } catch (error) {
    callbacks.onError?.(error instanceof Error ? error : new Error(String(error)));
  } finally {
    reader.releaseLock();
  }
}

/**
 * Fetch chart data for a specific ticker.
 */
export async function fetchChartForTicker(
  ticker: string,
  exchange: string = "NSE"
): Promise<StockChartOutput | null> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/chart/${ticker}?exchange=${exchange}`,
      { method: "GET" }
    );

    if (!response.ok) {
      console.error(`Failed to fetch chart for ${ticker}: ${response.status}`);
      return null;
    }

    const data = await response.json();
    return {
      ticker: data.ticker,
      company_name: data.company_name,
      current_price: data.current_price,
      price_change_percent: data.price_change_percent,
      chart_image: data.chart_image,
      historical_prices: data.historical_prices,
    };
  } catch (error) {
    console.error(`Error fetching chart for ${ticker}:`, error);
    return null;
  }
}
