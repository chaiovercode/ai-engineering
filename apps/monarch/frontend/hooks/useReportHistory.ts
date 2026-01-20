"use client";

import { useState, useEffect, useCallback } from "react";
import {
  SavedReport,
  getReports,
  saveReport,
  updateReport,
  deleteReport,
} from "@/lib/storage";
import { generateTitle } from "@/lib/titleGenerator";

export interface UseReportHistoryReturn {
  reports: SavedReport[];
  saveCurrentReport: (data: {
    reportText: string;
    tone: string;
    linkedin: SavedReport["linkedin"];
    whatsapp: SavedReport["whatsapp"];
    detectedTickers?: string[];
    primaryChart?: SavedReport["primaryChart"];
    variantB?: SavedReport["variantB"];
  }) => SavedReport;
  loadReport: (id: string) => SavedReport | null;
  removeReport: (id: string) => void;
  updateReportTitle: (id: string, title: string) => void;
  updateReportVariantB: (id: string, variantB: SavedReport["variantB"]) => void;
  refreshReports: () => void;
}

export function useReportHistory(): UseReportHistoryReturn {
  const [reports, setReports] = useState<SavedReport[]>([]);

  const refreshReports = useCallback(() => {
    setReports(getReports());
  }, []);

  useEffect(() => {
    refreshReports();
  }, [refreshReports]);

  const saveCurrentReport = useCallback(
    (data: {
      reportText: string;
      tone: string;
      linkedin: SavedReport["linkedin"];
      whatsapp: SavedReport["whatsapp"];
      detectedTickers?: string[];
      primaryChart?: SavedReport["primaryChart"];
      variantB?: SavedReport["variantB"];
    }) => {
      const title = generateTitle(data.linkedin?.content || null, data.reportText);
      const saved = saveReport({ ...data, title });
      refreshReports();
      return saved;
    },
    [refreshReports]
  );

  const loadReport = useCallback(
    (id: string) => {
      return reports.find((r) => r.id === id) || null;
    },
    [reports]
  );

  const removeReport = useCallback(
    (id: string) => {
      deleteReport(id);
      refreshReports();
    },
    [refreshReports]
  );

  const updateReportTitle = useCallback(
    (id: string, title: string) => {
      updateReport(id, { title });
      refreshReports();
    },
    [refreshReports]
  );

  const updateReportVariantB = useCallback(
    (id: string, variantB: SavedReport["variantB"]) => {
      updateReport(id, { variantB });
      refreshReports();
    },
    [refreshReports]
  );

  return {
    reports,
    saveCurrentReport,
    loadReport,
    removeReport,
    updateReportTitle,
    updateReportVariantB,
    refreshReports,
  };
}
