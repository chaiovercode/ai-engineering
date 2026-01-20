from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Tone(str, Enum):
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    PUNCHY = "punchy"


class Variant(str, Enum):
    A = "A"
    B = "B"


class TransformRequest(BaseModel):
    report_text: str = Field(..., min_length=50, description="The IC research report text to transform")
    tone: Optional[Tone] = Field(default=Tone.PROFESSIONAL, description="The tone/style for the generated content")
    variant: Optional[Variant] = Field(default=Variant.A, description="The variant to generate (A=insight-focused, B=action-focused)")


class LinkedInOutput(BaseModel):
    content: str = Field(..., description="The LinkedIn post content")
    hashtags: list[str] = Field(default_factory=list, description="Relevant hashtags")
    character_count: int = Field(..., description="Total character count")


class NewsletterOutput(BaseModel):
    headline: str = Field(..., description="Attention-grabbing headline")
    thesis: str = Field(..., description="30-second investment thesis")
    key_points: list[str] = Field(default_factory=list, description="Key bullet points")
    call_to_action: str = Field(..., description="CTA for readers")


class WhatsAppOutput(BaseModel):
    formatted_message: str = Field(..., description="Message with WhatsApp formatting (*bold*, _italic_)")
    plain_text: str = Field(..., description="Plain text version without formatting")


class HistoricalPriceData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockChartOutput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: Optional[str] = Field(None, description="Company name")
    current_price: float = Field(..., description="Current stock price")
    price_change_percent: float = Field(..., description="Price change percentage")
    chart_image: str = Field(..., description="Base64 encoded PNG chart image")
    historical_prices: list[HistoricalPriceData] = Field(default_factory=list, description="Historical price data")


class TransformResponse(BaseModel):
    linkedin: LinkedInOutput
    newsletter: NewsletterOutput
    whatsapp: WhatsAppOutput
    detected_tickers: list[str] = Field(default_factory=list, description="Stock tickers detected in the report")
    primary_chart: Optional[StockChartOutput] = Field(None, description="Chart for the primary detected ticker")


class ErrorResponse(BaseModel):
    detail: str
