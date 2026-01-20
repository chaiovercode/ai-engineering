/**
 * Technical indicators utilities for stock chart analysis
 */

export interface HistoricalPrice {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/**
 * Calculate Simple Moving Average (SMA)
 * @param data Array of historical prices
 * @param period Number of periods for the moving average
 * @returns Array of SMA values (null for insufficient data points)
 */
export const calculateSMA = (
  data: HistoricalPrice[],
  period: number
): (number | null)[] => {
  if (!data || data.length === 0) return [];

  const result: (number | null)[] = [];

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else {
      const sum = data
        .slice(i - period + 1, i + 1)
        .reduce((acc, price) => acc + price.close, 0);
      result.push(sum / period);
    }
  }

  return result;
};

/**
 * Format volume number with Indian abbreviations (Cr, L, K)
 * @param volume Volume number
 * @returns Formatted string
 */
export const formatVolume = (volume: number): string => {
  if (volume >= 10000000) {
    return `${(volume / 10000000).toFixed(2)} Cr`;
  }
  if (volume >= 100000) {
    return `${(volume / 100000).toFixed(2)} L`;
  }
  if (volume >= 1000) {
    return `${(volume / 1000).toFixed(2)} K`;
  }
  return volume.toLocaleString('en-IN');
};

/**
 * Format price in Indian Rupees
 * @param price Price value
 * @returns Formatted price string
 */
export const formatPrice = (price: number): string => {
  return `₹${price.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
};

/**
 * Format percentage change
 * @param change Percentage change value
 * @returns Formatted percentage string with sign
 */
export const formatChange = (change: number): string => {
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(2)}%`;
};
