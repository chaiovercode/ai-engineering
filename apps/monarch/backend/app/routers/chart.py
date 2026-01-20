"""Chart API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.chart_service import get_chart_image, get_stock_data, format_ticker


router = APIRouter(prefix="/api/v1/chart", tags=["chart"])


class StockPriceData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class ChartResponse(BaseModel):
    ticker: str
    company_name: str | None
    current_price: float
    price_change_percent: float
    chart_image: str  # base64 encoded PNG
    historical_prices: list[StockPriceData]
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None


class StockDataResponse(BaseModel):
    ticker: str
    company_name: str | None
    current_price: float
    price_change_percent: float
    historical_prices: list[StockPriceData]
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None


@router.get("/{ticker}", response_model=ChartResponse)
async def get_stock_chart(
    ticker: str,
    period: str = Query(default="3mo", regex="^(1mo|3mo|6mo|1y|2y)$"),
    exchange: str = Query(default="NSE", regex="^(NSE|BSE)$"),
):
    """
    Get stock chart image and data for a ticker.

    Args:
        ticker: Stock ticker symbol (e.g., TATASTEEL, RELIANCE)
        period: Historical data period (1mo, 3mo, 6mo, 1y, 2y)
        exchange: Stock exchange (NSE or BSE)

    Returns:
        Chart image as base64 PNG plus stock data
    """
    chart_image, stock_data = await get_chart_image(ticker, period, exchange)

    if not stock_data:
        raise HTTPException(
            status_code=404,
            detail=f"Stock data not found for ticker: {ticker}"
        )

    if not chart_image:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate chart for ticker: {ticker}"
        )

    return ChartResponse(
        ticker=stock_data.ticker,
        company_name=stock_data.company_name,
        current_price=stock_data.current_price,
        price_change_percent=stock_data.price_change_percent,
        chart_image=chart_image,
        historical_prices=[
            StockPriceData(
                date=p.date,
                open=p.open,
                high=p.high,
                low=p.low,
                close=p.close,
                volume=p.volume,
            )
            for p in stock_data.historical_prices
        ],
        fifty_two_week_high=stock_data.fifty_two_week_high,
        fifty_two_week_low=stock_data.fifty_two_week_low,
    )


@router.get("/{ticker}/data", response_model=StockDataResponse)
async def get_stock_data_only(
    ticker: str,
    period: str = Query(default="3mo", regex="^(1mo|3mo|6mo|1y|2y)$"),
    exchange: str = Query(default="NSE", regex="^(NSE|BSE)$"),
):
    """
    Get stock data without chart image (lighter endpoint).

    Args:
        ticker: Stock ticker symbol
        period: Historical data period
        exchange: Stock exchange

    Returns:
        Stock data without chart image
    """
    formatted_ticker = format_ticker(ticker, exchange)
    stock_data = await get_stock_data(formatted_ticker, period)

    if not stock_data:
        raise HTTPException(
            status_code=404,
            detail=f"Stock data not found for ticker: {ticker}"
        )

    return StockDataResponse(
        ticker=stock_data.ticker,
        company_name=stock_data.company_name,
        current_price=stock_data.current_price,
        price_change_percent=stock_data.price_change_percent,
        historical_prices=[
            StockPriceData(
                date=p.date,
                open=p.open,
                high=p.high,
                low=p.low,
                close=p.close,
                volume=p.volume,
            )
            for p in stock_data.historical_prices
        ],
        fifty_two_week_high=stock_data.fifty_two_week_high,
        fifty_two_week_low=stock_data.fifty_two_week_low,
    )
