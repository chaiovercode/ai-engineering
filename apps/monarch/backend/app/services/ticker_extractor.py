"""Extract stock tickers from text content using hybrid validation."""

import re
from dataclasses import dataclass
import yfinance as yf


@dataclass
class ExtractedTicker:
    ticker: str
    exchange: str
    confidence: float
    match_text: str
    company_name: str | None = None


# Common English words that look like tickers but aren't
EXCLUDED_WORDS = {
    "CEO", "CFO", "CTO", "COO", "USD", "INR", "RBI", "GDP", "FII", "DII",
    "SIP", "NAV", "IPO", "FPO", "NPA", "EMI", "ROI", "ROE", "EPS", "PBT",
    "PAT", "EBITDA", "QOQ", "YOY", "MOM", "ETF", "PSU", "NBFCs", "NBFC",
    "API", "CPI", "WPI", "GST", "TDS", "PAN", "KYC", "AUM", "AMC", "SEBI",
    "NSE", "BSE", "MCX", "NSDL", "CDSL", "ASBA", "OFS", "QIP", "FDI",
    "INDIA", "THE", "FOR", "AND", "WITH", "FROM", "HAVE", "THIS", "THAT",
    "WILL", "ARE", "WAS", "WERE", "BEEN", "HAS", "HAD", "MAY", "CAN",
    "SHOULD", "WOULD", "COULD", "ABOUT", "INTO", "OVER", "AFTER", "BEFORE",
    "BETWEEN", "THROUGH", "DURING", "UNDER", "AGAIN", "FURTHER", "THEN",
    "ONCE", "HERE", "THERE", "WHEN", "WHERE", "WHY", "HOW", "ALL", "EACH",
    "BOTH", "FEW", "MORE", "MOST", "OTHER", "SOME", "SUCH", "ONLY", "OWN",
    "SAME", "THAN", "TOO", "VERY", "JUST", "ALSO", "NOW", "NEW", "OLD",
    "HIGH", "LOW", "GOOD", "BAD", "LONG", "SHORT", "BIG", "SMALL", "SAYS",
    "SAID", "GROWTH", "MARKET", "STOCK", "STOCKS", "SHARE", "SHARES",
    "BUDGET", "INDIAN", "GLOBAL", "ECONOMY", "ECONOMIC", "FISCAL",
    "POLICY", "REFORM", "REFORMS", "SECTOR", "SECTORS", "BANK", "BANKS",
    "DEFENCE", "DEFENSE", "EXPORT", "EXPORTS", "IMPORT", "IMPORTS",
    "EXPECTED", "FOCUSED", "FRIENDLY", "DOMESTIC", "CONSUMPTION",
}

# Known valid Indian stock tickers (fast lookup, no API needed)
KNOWN_TICKERS = {
    # Nifty 50 components
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR",
    "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK", "LT", "HCLTECH",
    "AXISBANK", "ASIANPAINT", "MARUTI", "BAJFINANCE", "SUNPHARMA",
    "TITAN", "ULTRACEMCO", "ONGC", "NTPC", "TATASTEEL", "POWERGRID",
    "M&M", "JSWSTEEL", "ADANIENT", "ADANIPORTS", "COALINDIA", "WIPRO",
    "TATAMOTORS", "NESTLEIND", "DIVISLAB", "GRASIM", "BAJAJFINSV",
    "TECHM", "BRITANNIA", "HINDALCO", "INDUSINDBK", "DRREDDY",
    "CIPLA", "EICHERMOT", "APOLLOHOSP", "BPCL", "HEROMOTOCO",
    "TATACONSUM", "UPL", "SBILIFE", "LTIM", "HDFCLIFE",
    # Nifty Next 50 / Popular large-caps
    "HAVELLS", "PIDILITIND", "DABUR", "GODREJCP", "MARICO", "COLPAL",
    "BERGEPAINT", "VOLTAS", "CROMPTON", "WHIRLPOOL", "BLUESTARCO",
    "SIEMENS", "ABB", "BHEL", "CUMMINSIND", "THERMAX", "ESCORTS",
    "BOSCHLTD", "MOTHERSON", "BHARATFORG", "AMARAJABAT", "EXIDEIND",
    "MUTHOOTFIN", "BAJAJHLDNG", "CHOLAFIN", "MANAPPURAM", "LICHSGFIN",
    "RECLTD", "PFC", "IDFCFIRSTB", "FEDERALBNK", "RBLBANK", "BANDHANBNK",
    "AUBANK", "YESBANK", "IDBI", "KALYANKJIL", "BATAINDIA", "PAGEIND",
    "AUROPHARMA", "BIOCON", "LUPIN", "TORNTPHARM", "ALKEM", "IPCALAB",
    "LAURUSLABS", "GLENMARK", "NATCOPHARM", "ABBOTINDIA", "SYNGENE",
    "DLF", "GODREJPROP", "OBEROIRLTY", "PRESTIGE", "BRIGADE", "SOBHA",
    "PHOENIXLTD", "LODHA", "MAHLIFE",
    # Popular mid-caps and small-caps
    "IRCTC", "ZOMATO", "PAYTM", "NYKAA", "POLICYBZR", "DELHIVERY",
    "TRENT", "HAL", "BEL", "IRFC", "RVNL", "NHPC", "SJVN",
    "PNB", "BANKBARODA", "CANBK", "UNIONBANK", "IOB", "CENTRALBK",
    "JNKINDIA", "JNK", "JINDALSTEL", "VEDL", "NMDC", "SAIL",
    "COCHINSHIP", "GRSE", "MAZAGON", "GARDENREACH", "BDL", "BEML",
    "BHEL", "NBCC", "NCC", "KPITTECH", "PERSISTENT", "COFORGE",
    "MPHASIS", "LTTS", "TATAELXSI", "CYIENT", "HAPPSTMNDS",
    "DEEPAKNTR", "PIIND", "ATUL", "NAVINFLUOR", "SRF", "FLUOROCHEM",
    "AARTIIND", "CLEAN", "ALKYLAMINE", "GMMPFAUDLR",
    "TATAPOWER", "ADANIGREEN", "ADANIPOWER", "JSWENERGY", "TORNTPOWER",
    "CESC", "TATACOMM", "BHARTIHEXA", "INDIAMART", "JUSTDIAL", "NAUKRI",
    # Brokerages and financial services
    "MONARCH", "MOFSL", "ABORANGE", "GEOJITFSL", "IIFL", "ANGELONE",
    "ICICIPRULI", "HDFCAMC", "NIPPONIND", "UTIAMC",
    # ETFs
    "NIFTYBEES", "BANKBEES", "GOLDBEES", "LIQUIDBEES",
    # Other popular stocks
    "ADANIWILMAR", "AWL", "ZYDUSLIFE", "MAXHEALTH", "FORTIS", "MEDANTA",
    "RAINBOW", "METROPOLIS", "DMART", "AVENUE", "TATATECH", "KAYNES",
    "DIXON", "AMBER", "AFFLE", "ROUTE", "HAPPIEST", "CAMPUS", "DEVYANI",
}

# Company name to ticker mapping
NAME_TO_TICKER = {
    "reliance": "RELIANCE",
    "reliance industries": "RELIANCE",
    "tata steel": "TATASTEEL",
    "tata motors": "TATAMOTORS",
    "infosys": "INFY",
    "hdfc bank": "HDFCBANK",
    "icici bank": "ICICIBANK",
    "state bank": "SBIN",
    "sbi": "SBIN",
    "bajaj finance": "BAJFINANCE",
    "monarch": "MONARCH",
    "monarch networth": "MONARCH",
    "monarch networth capital": "MONARCH",
    "mncl": "MONARCH",
}

# Cache for yfinance validated tickers
_validated_ticker_cache: dict[str, tuple[bool, str | None]] = {}


def validate_ticker_with_yfinance(ticker: str, exchange: str = "NSE") -> tuple[bool, str | None]:
    """
    Validate if a ticker exists on NSE/BSE using yfinance.
    Returns (is_valid, company_name). Only used for unknown tickers.
    """
    cache_key = f"{ticker}.{exchange}"
    if cache_key in _validated_ticker_cache:
        return _validated_ticker_cache[cache_key]

    # Try NSE first, then BSE
    suffixes = [".NS", ".BO"] if exchange == "NSE" else [".BO", ".NS"]

    for suffix in suffixes:
        try:
            stock = yf.Ticker(f"{ticker}{suffix}")
            info = stock.info
            # Check if we got valid data (not an error response)
            if info and info.get("regularMarketPrice") is not None:
                company_name = info.get("shortName") or info.get("longName")
                _validated_ticker_cache[cache_key] = (True, company_name)
                return True, company_name
        except Exception:
            continue

    _validated_ticker_cache[cache_key] = (False, None)
    return False, None


def extract_tickers(text: str) -> list[ExtractedTicker]:
    """
    Extract stock tickers from text using hybrid validation.
    First checks known tickers (fast), then optionally validates unknown ones via yfinance.
    Returns list of validated tickers sorted by confidence.
    """
    tickers: list[ExtractedTicker] = []
    seen_tickers: set[str] = set()

    # Strategy 1: Direct ticker symbols with exchange suffix (highest confidence)
    # Pattern: RELIANCE.NS, TATASTEEL.BO, etc.
    exchange_pattern = r'\b([A-Z][A-Z0-9&]{2,15})\.(NS|BO)\b'
    for match in re.finditer(exchange_pattern, text):
        ticker = match.group(1)
        exchange = "NSE" if match.group(2) == "NS" else "BSE"
        if ticker not in seen_tickers and ticker not in EXCLUDED_WORDS:
            seen_tickers.add(ticker)
            tickers.append(ExtractedTicker(
                ticker=ticker,
                exchange=exchange,
                confidence=1.0,
                match_text=match.group(0)
            ))

    # Strategy 2: Known ticker symbols (fast lookup, no API call)
    ticker_pattern = r'\b([A-Z][A-Z0-9&]{2,14})\b'
    for match in re.finditer(ticker_pattern, text):
        ticker = match.group(1)
        if ticker not in seen_tickers and ticker not in EXCLUDED_WORDS and ticker in KNOWN_TICKERS:
            seen_tickers.add(ticker)
            tickers.append(ExtractedTicker(
                ticker=ticker,
                exchange="NSE",
                confidence=0.9,
                match_text=match.group(0)
            ))

    # Strategy 3: Company name mentions (case-insensitive)
    text_lower = text.lower()
    for name, ticker in NAME_TO_TICKER.items():
        if name in text_lower and ticker not in seen_tickers:
            idx = text_lower.find(name)
            match_text = text[idx:idx + len(name)]
            seen_tickers.add(ticker)
            tickers.append(ExtractedTicker(
                ticker=ticker,
                exchange="NSE",
                confidence=0.85,
                match_text=match_text
            ))

    # Strategy 4: Pattern "X as the symbol" (explicit symbol mention)
    symbol_pattern = r'([A-Z][A-Z0-9&]{2,14})\s+as\s+the\s+symbol'
    for match in re.finditer(symbol_pattern, text, re.IGNORECASE):
        ticker = match.group(1).upper()
        if ticker not in seen_tickers and ticker not in EXCLUDED_WORDS:
            seen_tickers.add(ticker)
            # Add to known tickers dynamically for this session
            KNOWN_TICKERS.add(ticker)
            tickers.append(ExtractedTicker(
                ticker=ticker,
                exchange="NSE",
                confidence=0.95,
                match_text=match.group(0)
            ))

    # Sort by confidence (highest first)
    tickers.sort(key=lambda x: -x.confidence)

    return tickers


def get_primary_ticker(text: str) -> tuple[str | None, str]:
    """
    Extract the primary (most likely) ticker from text.
    Returns tuple of (ticker, exchange) or (None, "NSE") if not found.
    """
    tickers = extract_tickers(text)
    if tickers:
        return tickers[0].ticker, tickers[0].exchange
    return None, "NSE"


def get_all_tickers(text: str) -> list[str]:
    """
    Extract all unique tickers from text.
    Returns list of ticker symbols without exchange suffix.
    """
    tickers = extract_tickers(text)
    return [t.ticker for t in tickers]
