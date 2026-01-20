"use client";

import { useState, useMemo } from "react";
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
} from "recharts";
import { calculateSMA, formatVolume, formatPrice, formatChange, type HistoricalPrice } from "@/utils/technicalIndicators";

export interface StockChartData {
  ticker: string;
  company_name: string | null;
  current_price: number;
  price_change_percent: number;
  chart_image?: string;
  historical_prices?: HistoricalPrice[];
}

interface StockChartProps {
  data: StockChartData;
  showInteractive?: boolean;
}

type TimeRange = "1M" | "3M" | "6M" | "1Y";

const TIME_RANGES: { value: TimeRange; label: string; days: number }[] = [
  { value: "1M", label: "1M", days: 22 },
  { value: "3M", label: "3M", days: 66 },
  { value: "6M", label: "6M", days: 132 },
  { value: "1Y", label: "1Y", days: 252 },
];

// Custom tooltip component
interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload?: { close?: number; open?: number; high?: number; low?: number; volume?: number } }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0]?.payload;
  if (!data) return null;

  return (
    <div className="bg-[#1a1a1a] border border-[#333] p-3 text-sm">
      <p className="text-white font-semibold mb-1">{label}</p>
      {data.close !== undefined && <p className="text-[#c9a227]">Close: {formatPrice(data.close)}</p>}
      {data.open !== undefined && <p className="text-gray-400">Open: {formatPrice(data.open)}</p>}
      {data.high !== undefined && <p className="text-green-500">High: {formatPrice(data.high)}</p>}
      {data.low !== undefined && <p className="text-red-500">Low: {formatPrice(data.low)}</p>}
      {data.volume !== undefined && <p className="text-gray-400">Vol: {formatVolume(data.volume)}</p>}
    </div>
  );
}

export function StockChart({ data, showInteractive = true }: StockChartProps) {
  const [selectedRange, setSelectedRange] = useState<TimeRange>("3M");
  const [showSMA20, setShowSMA20] = useState(false);
  const [showSMA50, setShowSMA50] = useState(false);

  // Clean ticker display (remove suffix)
  const displayTicker = data.ticker?.replace(".NS", "").replace(".BO", "") || "";
  const isPositive = data.price_change_percent >= 0;

  // Filter data based on selected time range
  const filteredData = useMemo(() => {
    if (!data.historical_prices?.length) return [];

    const range = TIME_RANGES.find((r) => r.value === selectedRange);
    const daysToShow = range?.days || 66;
    const sliced = data.historical_prices.slice(-Math.min(daysToShow, data.historical_prices.length));

    return sliced.map((price) => {
      const d = new Date(price.date);
      const day = d.getDate();
      const month = d.toLocaleString("en-US", { month: "short" });
      return {
        date: `${day} ${month}`,
        open: price.open,
        high: price.high,
        low: price.low,
        close: price.close,
        volume: price.volume,
      };
    });
  }, [data.historical_prices, selectedRange]);

  // Calculate SMAs
  const chartDataWithSMA = useMemo(() => {
    if (!data.historical_prices?.length || !filteredData.length) return filteredData;

    const sma20 = showSMA20 ? calculateSMA(data.historical_prices, 20) : [];
    const sma50 = showSMA50 ? calculateSMA(data.historical_prices, 50) : [];

    return filteredData.map((item, index) => {
      const smaIndex = data.historical_prices!.length - filteredData.length + index;
      return {
        ...item,
        sma20: sma20[smaIndex] || null,
        sma50: sma50[smaIndex] || null,
      };
    });
  }, [data.historical_prices, filteredData, showSMA20, showSMA50]);

  // Determine chart trend color
  const periodIsPositive = useMemo(() => {
    if (filteredData.length < 2) return isPositive;
    return filteredData[filteredData.length - 1].close >= filteredData[0].close;
  }, [filteredData, isPositive]);

  const trendColor = periodIsPositive ? "#00d395" : "#ff4757";

  // If no historical data, show static chart image
  if (!data.historical_prices?.length && data.chart_image) {
    return (
      <div className="bg-[#0f0f0f] p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-bold text-white">{displayTicker}</h3>
            {data.company_name && (
              <p className="text-sm text-gray-500">{data.company_name}</p>
            )}
          </div>
          <div className="text-right">
            <p className="text-xl font-bold text-white">
              {formatPrice(data.current_price)}
            </p>
            <p className={`text-sm font-semibold ${isPositive ? "text-green-500" : "text-red-500"}`}>
              {isPositive ? "▲" : "▼"} {formatChange(data.price_change_percent)}
            </p>
          </div>
        </div>

        {/* Static chart image */}
        <img
          src={`data:image/png;base64,${data.chart_image}`}
          alt={`${displayTicker} stock chart`}
          className="w-full"
        />
      </div>
    );
  }

  // If no data at all, show placeholder
  if (!data.historical_prices?.length) {
    return (
      <div className="bg-[#0f0f0f] p-6 flex items-center justify-center h-[300px]">
        <p className="text-gray-500">No chart data available</p>
      </div>
    );
  }

  return (
    <div className="bg-[#0f0f0f] p-4">
      {/* Header - only show when not interactive (static mode) */}
      {!showInteractive && (
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-bold text-white">{displayTicker}</h3>
            {data.company_name && (
              <p className="text-sm text-gray-500">{data.company_name}</p>
            )}
          </div>
          <div className="text-right">
            <p className="text-xl font-bold text-white">
              {formatPrice(data.current_price)}
            </p>
            <p className={`text-sm font-semibold ${isPositive ? "text-green-500" : "text-red-500"}`}>
              {isPositive ? "▲" : "▼"} {formatChange(data.price_change_percent)}
            </p>
          </div>
        </div>
      )}

      {showInteractive && (
        <>
          {/* Time Range Filters */}
          <div className="flex items-center gap-2 mb-4">
            {TIME_RANGES.map((range) => (
              <button
                key={range.value}
                onClick={() => setSelectedRange(range.value)}
                className={`px-3 py-1.5 text-xs font-semibold transition-all ${
                  selectedRange === range.value
                    ? "bg-[#c9a227] text-black"
                    : "bg-[#1a1a1a] text-gray-400 hover:bg-[#252525]"
                }`}
              >
                {range.label}
              </button>
            ))}
          </div>

          {/* SMA Toggles */}
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xs text-gray-500">Indicators:</span>
            <button
              onClick={() => setShowSMA20(!showSMA20)}
              className={`px-3 py-1 text-xs font-semibold transition-all flex items-center gap-1 ${
                showSMA20
                  ? "bg-orange-500 text-white"
                  : "bg-[#1a1a1a] text-gray-400 hover:bg-[#252525]"
              }`}
            >
              <span className={`w-3 h-0.5 ${showSMA20 ? "bg-white" : "bg-orange-500"}`} />
              SMA 20
            </button>
            <button
              onClick={() => setShowSMA50(!showSMA50)}
              className={`px-3 py-1 text-xs font-semibold transition-all flex items-center gap-1 ${
                showSMA50
                  ? "bg-blue-500 text-white"
                  : "bg-[#1a1a1a] text-gray-400 hover:bg-[#252525]"
              }`}
            >
              <span className={`w-3 h-0.5 ${showSMA50 ? "bg-white" : "bg-blue-500"}`} />
              SMA 50
            </button>
          </div>
        </>
      )}

      {/* Chart */}
      <div className="h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartDataWithSMA} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={trendColor} stopOpacity={0.3} />
                <stop offset="95%" stopColor={trendColor} stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" opacity={0.5} />

            <XAxis
              dataKey="date"
              stroke="#666"
              tick={{ fill: "#666", fontSize: 10 }}
              tickLine={{ stroke: "#333" }}
              interval="preserveStartEnd"
            />

            <YAxis
              yAxisId="price"
              orientation="right"
              stroke="#666"
              tick={{ fill: "#666", fontSize: 10 }}
              tickLine={{ stroke: "#333" }}
              tickFormatter={(value) => `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`}
              domain={["auto", "auto"]}
            />

            <YAxis
              yAxisId="volume"
              orientation="left"
              stroke="#666"
              tick={false}
              tickLine={false}
              axisLine={false}
              domain={[0, (dataMax: number) => dataMax * 4]}
            />

            <Tooltip content={<CustomTooltip />} />

            {/* Volume bars */}
            <Bar
              yAxisId="volume"
              dataKey="volume"
              fill="#333"
              opacity={0.3}
            />

            {/* Price area */}
            <Area
              yAxisId="price"
              type="monotone"
              dataKey="close"
              stroke={trendColor}
              strokeWidth={2}
              fill="url(#colorPrice)"
            />

            {/* SMA lines */}
            {showSMA20 && (
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="sma20"
                stroke="#ffa502"
                strokeWidth={1.5}
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
                strokeWidth={1.5}
                dot={false}
                connectNulls
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// Export component for rendering as static image in carousel
export function StockChartStatic({ data }: { data: StockChartData }) {
  return <StockChart data={data} showInteractive={false} />;
}
