// localStorage wrapper for report history persistence

export interface SavedStockChart {
  ticker: string;
  company_name: string | null;
  current_price: number;
  price_change_percent: number;
  chart_image: string;
}

export interface SavedReport {
  id: string;
  title: string;
  createdAt: number;
  reportText: string;
  tone: string;
  linkedin: {
    content: string;
    hashtags: string[];
    character_count: number;
  } | null;
  whatsapp: {
    formatted_message: string;
    plain_text: string;
  } | null;
  detectedTickers?: string[];
  primaryChart?: SavedStockChart | null;
  variantB?: {
    linkedin: {
      content: string;
      hashtags: string[];
      character_count: number;
    } | null;
    whatsapp: {
      formatted_message: string;
      plain_text: string;
    } | null;
    detectedTickers?: string[];
    primaryChart?: SavedStockChart | null;
  };
}

const STORAGE_KEY = "monarch_report_history";
const MAX_REPORTS = 50;

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

export function getReports(): SavedReport[] {
  if (typeof window === "undefined") return [];
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (!data) return [];
    return JSON.parse(data);
  } catch {
    return [];
  }
}

export function saveReport(report: Omit<SavedReport, "id" | "createdAt">): SavedReport {
  const reports = getReports();
  const newReport: SavedReport = {
    ...report,
    id: generateId(),
    createdAt: Date.now(),
  };

  // Add to beginning, limit total
  const updated = [newReport, ...reports].slice(0, MAX_REPORTS);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));

  return newReport;
}

export function updateReport(id: string, updates: Partial<SavedReport>): SavedReport | null {
  const reports = getReports();
  const index = reports.findIndex((r) => r.id === id);
  if (index === -1) return null;

  const updated = { ...reports[index], ...updates };
  reports[index] = updated;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(reports));

  return updated;
}

export function deleteReport(id: string): boolean {
  const reports = getReports();
  const filtered = reports.filter((r) => r.id !== id);
  if (filtered.length === reports.length) return false;

  localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  return true;
}

export function clearAllReports(): void {
  localStorage.removeItem(STORAGE_KEY);
}
