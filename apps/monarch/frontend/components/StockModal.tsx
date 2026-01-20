"use client";

import { useState, useEffect, useMemo } from "react";
import {
  ComposedChart,
  Area,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { calculateSMA, formatVolume, formatPrice, formatChange, type HistoricalPrice } from "@/utils/technicalIndicators";

interface StockModalProps {
  isOpen: boolean;
  onClose: () => void;
  ticker: string;
  companyName: string | null;
  currentPrice: number;
  priceChangePercent: number;
  historicalPrices: HistoricalPrice[];
}

type TimeRange = "1M" | "3M" | "6M" | "1Y";

const TIME_RANGES: { value: TimeRange; label: string; days: number }[] = [
  { value: "1M", label: "1M", days: 22 },
  { value: "3M", label: "3M", days: 66 },
  { value: "6M", label: "6M", days: 132 },
  { value: "1Y", label: "1Y", days: 252 },
];

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload?: { close?: number; open?: number; high?: number; low?: number; volume?: number; date?: string } }>;
  label?: string;
}

function ChartTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0]?.payload;
  if (!data) return null;

  return (
    <div className="bg-[#1a1a1a] border border-[#333] px-4 py-3 shadow-xl">
      <p className="text-white font-bold text-sm mb-2">{data.date}</p>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
        {data.open !== undefined && (
          <>
            <span className="text-gray-500">Open</span>
            <span className="text-white text-right">{formatPrice(data.open)}</span>
          </>
        )}
        {data.high !== undefined && (
          <>
            <span className="text-gray-500">High</span>
            <span className="text-green-400 text-right">{formatPrice(data.high)}</span>
          </>
        )}
        {data.low !== undefined && (
          <>
            <span className="text-gray-500">Low</span>
            <span className="text-red-400 text-right">{formatPrice(data.low)}</span>
          </>
        )}
        {data.close !== undefined && (
          <>
            <span className="text-gray-500">Close</span>
            <span className="text-[#c9a227] text-right font-semibold">{formatPrice(data.close)}</span>
          </>
        )}
        {data.volume !== undefined && (
          <>
            <span className="text-gray-500">Volume</span>
            <span className="text-white text-right">{formatVolume(data.volume)}</span>
          </>
        )}
      </div>
    </div>
  );
}

export function StockModal({
  isOpen,
  onClose,
  ticker,
  companyName,
  currentPrice,
  priceChangePercent,
  historicalPrices,
}: StockModalProps) {
  const [selectedRange, setSelectedRange] = useState<TimeRange>("3M");
  const [showSMA20, setShowSMA20] = useState(true);
  const [showSMA50, setShowSMA50] = useState(false);

  const displayTicker = ticker?.replace(".NS", "").replace(".BO", "") || "";
  const isPositive = priceChangePercent >= 0;

  // Close on escape
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.addEventListener("keydown", handleEsc);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEsc);
      document.body.style.overflow = "";
    };
  }, [isOpen, onClose]);

  // Filter data based on selected time range
  const filteredData = useMemo(() => {
    if (!historicalPrices?.length) return [];
    const range = TIME_RANGES.find((r) => r.value === selectedRange);
    const daysToShow = range?.days || 66;
    const sliced = historicalPrices.slice(-Math.min(daysToShow, historicalPrices.length));

    return sliced.map((price) => {
      const d = new Date(price.date);
      const day = d.getDate();
      const month = d.toLocaleString("en-US", { month: "short" });
      return {
        date: `${day} ${month}`,
        fullDate: price.date,
        open: price.open,
        high: price.high,
        low: price.low,
        close: price.close,
        volume: price.volume,
      };
    });
  }, [historicalPrices, selectedRange]);

  // Calculate SMAs
  const chartDataWithSMA = useMemo(() => {
    if (!historicalPrices?.length || !filteredData.length) return filteredData;

    const sma20 = showSMA20 ? calculateSMA(historicalPrices, 20) : [];
    const sma50 = showSMA50 ? calculateSMA(historicalPrices, 50) : [];

    return filteredData.map((item, index) => {
      const smaIndex = historicalPrices.length - filteredData.length + index;
      return {
        ...item,
        sma20: sma20[smaIndex] || null,
        sma50: sma50[smaIndex] || null,
      };
    });
  }, [historicalPrices, filteredData, showSMA20, showSMA50]);

  // Period performance
  const periodStats = useMemo(() => {
    if (filteredData.length < 2) return null;
    const first = filteredData[0].close;
    const last = filteredData[filteredData.length - 1].close;
    const change = ((last - first) / first) * 100;
    const high = Math.max(...filteredData.map((d) => d.high));
    const low = Math.min(...filteredData.map((d) => d.low));
    const avgVolume = filteredData.reduce((sum, d) => sum + d.volume, 0) / filteredData.length;
    return { change, high, low, avgVolume, periodPositive: change >= 0 };
  }, [filteredData]);

  const trendColor = periodStats?.periodPositive ? "#00d395" : "#ff4757";

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-5xl mx-4 max-h-[90vh] flex flex-col bg-[#0a0a0a] border-2 border-[#1a1a1a] shadow-2xl">
        {/* Header - Fixed */}
        <div className="border-b border-[#1a1a1a] flex-shrink-0">
          <div className="px-8 py-6 flex items-start justify-between">
            {/* Left: Ticker info */}
            <div className="flex items-center gap-5">
              <div className="w-16 h-16 bg-[#c9a227] flex items-center justify-center">
                <span className="text-[#0a0a0a] font-black text-xl">
                  {displayTicker.slice(0, 2)}
                </span>
              </div>
              <div>
                <h2 className="text-3xl font-black text-white tracking-tight">
                  {displayTicker}
                </h2>
                {companyName && (
                  <p className="text-sm text-gray-500 mt-1">{companyName}</p>
                )}
              </div>
            </div>

            {/* Right: Price + Close button */}
            <div className="flex items-start gap-6">
              <div className="text-right">
                <p className="text-4xl font-black text-white tracking-tight">
                  {formatPrice(currentPrice)}
                </p>
                <div
                  className={`inline-flex items-center gap-2 mt-2 px-4 py-1.5 ${
                    isPositive ? "bg-green-500/20" : "bg-red-500/20"
                  }`}
                >
                  <span className={`text-xl ${isPositive ? "text-green-400" : "text-red-400"}`}>
                    {isPositive ? "▲" : "▼"}
                  </span>
                  <span className={`text-xl font-bold ${isPositive ? "text-green-400" : "text-red-400"}`}>
                    {formatChange(priceChangePercent)}
                  </span>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-gray-500 hover:text-white hover:bg-[#1a1a1a] transition-colors"
              >
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Controls row */}
          <div className="px-8 pb-4 flex items-center justify-between">
            {/* Time range */}
            <div className="flex items-center gap-2">
              {TIME_RANGES.map((range) => (
                <button
                  key={range.value}
                  onClick={() => setSelectedRange(range.value)}
                  className={`px-4 py-2 text-sm font-bold transition-all ${
                    selectedRange === range.value
                      ? "bg-[#c9a227] text-[#0a0a0a]"
                      : "bg-[#1a1a1a] text-gray-400 hover:bg-[#252525] hover:text-white"
                  }`}
                >
                  {range.label}
                </button>
              ))}
            </div>

            {/* Indicators */}
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-600 uppercase tracking-wider">Indicators</span>
              <button
                onClick={() => setShowSMA20(!showSMA20)}
                className={`px-4 py-2 text-sm font-bold transition-all flex items-center gap-2 ${
                  showSMA20
                    ? "bg-orange-500 text-white"
                    : "bg-[#1a1a1a] text-gray-400 hover:bg-[#252525]"
                }`}
              >
                <span className={`w-4 h-0.5 ${showSMA20 ? "bg-white" : "bg-orange-500"}`} />
                SMA 20
              </button>
              <button
                onClick={() => setShowSMA50(!showSMA50)}
                className={`px-4 py-2 text-sm font-bold transition-all flex items-center gap-2 ${
                  showSMA50
                    ? "bg-blue-500 text-white"
                    : "bg-[#1a1a1a] text-gray-400 hover:bg-[#252525]"
                }`}
              >
                <span className={`w-4 h-0.5 ${showSMA50 ? "bg-white" : "bg-blue-500"}`} />
                SMA 50
              </button>
            </div>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto">
          {/* Chart */}
          <div className="p-6">
            <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartDataWithSMA} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <defs>
                  <linearGradient id="modalColorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={trendColor} stopOpacity={0.4} />
                    <stop offset="95%" stopColor={trendColor} stopOpacity={0} />
                  </linearGradient>
                </defs>

                <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />

                <XAxis
                  dataKey="date"
                  stroke="#333"
                  tick={{ fill: "#666", fontSize: 11 }}
                  tickLine={{ stroke: "#333" }}
                  axisLine={{ stroke: "#333" }}
                />

                <YAxis
                  yAxisId="price"
                  orientation="right"
                  stroke="#333"
                  tick={{ fill: "#666", fontSize: 11 }}
                  tickLine={{ stroke: "#333" }}
                  axisLine={{ stroke: "#333" }}
                  tickFormatter={(value) => `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`}
                  domain={["auto", "auto"]}
                />

                <YAxis
                  yAxisId="volume"
                  orientation="left"
                  stroke="#333"
                  tick={false}
                  tickLine={false}
                  axisLine={false}
                  domain={[0, (dataMax: number) => dataMax * 4]}
                />

                <Tooltip content={<ChartTooltip />} />

                {/* Current price reference line */}
                <ReferenceLine
                  yAxisId="price"
                  y={currentPrice}
                  stroke="#c9a227"
                  strokeDasharray="5 5"
                  strokeOpacity={0.5}
                />

                {/* Volume bars */}
                <Bar yAxisId="volume" dataKey="volume" fill="#252525" opacity={0.6} />

                {/* Price area */}
                <Area
                  yAxisId="price"
                  type="monotone"
                  dataKey="close"
                  stroke={trendColor}
                  strokeWidth={2.5}
                  fill="url(#modalColorPrice)"
                />

                {/* SMA lines */}
                {showSMA20 && (
                  <Line
                    yAxisId="price"
                    type="monotone"
                    dataKey="sma20"
                    stroke="#ffa502"
                    strokeWidth={2}
                    dot={false}
                    connectNulls
                  />
                )}

                {showSMA50 && (
                  <Line
                    yAxisId="price"
                    type="monotone"
                    dataKey="sma50"
                    stroke="#5b8ef4"
                    strokeWidth={2}
                    dot={false}
                    connectNulls
                  />
                )}
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Stats row */}
        {periodStats && (
          <div className="px-8 pb-6">
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-[#111] p-4 border border-[#1a1a1a]">
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-1">Period Change</p>
                <p className={`text-xl font-bold ${periodStats.periodPositive ? "text-green-400" : "text-red-400"}`}>
                  {periodStats.periodPositive ? "+" : ""}{periodStats.change.toFixed(2)}%
                </p>
              </div>
              <div className="bg-[#111] p-4 border border-[#1a1a1a]">
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-1">Period High</p>
                <p className="text-xl font-bold text-green-400">{formatPrice(periodStats.high)}</p>
              </div>
              <div className="bg-[#111] p-4 border border-[#1a1a1a]">
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-1">Period Low</p>
                <p className="text-xl font-bold text-red-400">{formatPrice(periodStats.low)}</p>
              </div>
              <div className="bg-[#111] p-4 border border-[#1a1a1a]">
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-1">Avg Volume</p>
                <p className="text-xl font-bold text-white">{formatVolume(periodStats.avgVolume)}</p>
              </div>
            </div>
          </div>
        )}

        </div>
        {/* End scrollable content */}

        {/* Footer - Fixed */}
        <div className="px-8 py-4 border-t border-[#1a1a1a] flex items-center justify-between flex-shrink-0">
          <p className="text-xs text-gray-600">Data from Yahoo Finance • Press ESC to close</p>
          <div className="flex items-center gap-2">
            <img src="/mncl-logo.svg" alt="Monarch" className="h-5 w-auto opacity-50" />
          </div>
        </div>
      </div>
    </div>
  );
}
