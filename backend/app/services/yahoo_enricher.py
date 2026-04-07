import yfinance as yf
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd


def safe_decimal(value):
    try:
        if value is None:
            return None
        return Decimal(str(value))
    except:
        return None


def parse_price(value):
    if not value:
        return None
    try:
        return Decimal(str(value).replace("$", "").replace(",", ""))
    except:
        return None


def parse_date(value):
    if not value:
        return None
    val_str = str(value).strip()
    try:
        # Jeśli string jest długi, zawiera godzinę
        if len(val_str) > 10:
            return datetime.strptime(val_str, "%Y-%m-%d %H:%M:%S")
        return datetime.strptime(val_str, "%Y-%m-%d")
    except:
        return None


def enrich_trade(trade_raw):
    """
    trade_raw: TradeRaw SQLAlchemy object
    """

    payload = trade_raw.payload

    ticker = payload.get("Ticker")
    insider = payload.get("Insider")
    filing_date_raw = payload.get("FilingDate")
    trade_date_raw = payload.get("TradeDate")
    value_raw = payload.get("Value")
    price_raw = payload.get("PriceReported")

    filing_date = parse_date(filing_date_raw)
    trade_date = parse_date(trade_date_raw)

    value = parse_price(value_raw)
    price_reported = parse_price(price_raw)

    if not ticker:
        return None

    try:
        ticker_yf = yf.Ticker(ticker)

        hist = ticker_yf.history(
            start=trade_date,
            end=trade_date + timedelta(days=1)
        )

        if hist.empty:
            return None

        low_trade_day = hist["Low"].iloc[0]
        high_trade_day = hist["High"].iloc[0]



        # OHLC JSON
        hist_reset = hist.reset_index()

        # konwersja Timestamp → string
        hist_reset["Date"] = hist_reset["Date"].astype(str)
        hist_recent = ticker_yf.history(period="1d")
        price_filling = hist_recent["Close"].iloc[-1]

        ohlc_json = hist_reset.to_dict(orient="records")
        hist_full = ticker_yf.history(period="max")
        if hist_full.empty:
            ticker_age_days = None
        else:
            first_date = hist_full.index.min()
            if first_date.tzinfo is not None:
                first_date = first_date.tz_convert(None)

            ticker_age_days = (datetime.utcnow() - first_date.to_pydatetime()).days

    except Exception as e:
        print(f"YAHOO ERROR for {ticker}: {e}")
        return None

    return {
        # 🔵 CORE FIELDS
        "Ticker": ticker,
        "Insider": insider,
        "FilingDate": filing_date,
        "TradeDate": trade_date,

        # 🔵 PRICE DATA
        "PriceReported": safe_decimal(price_reported),
        "LowTradeDay": safe_decimal(low_trade_day),
        "HighTradeDay": safe_decimal(high_trade_day),
        "TickerAgeDays": ticker_age_days,
        "OHLCJson": ohlc_json,
        "Value": safe_decimal(value),
        "Price": safe_decimal(price_reported),
        "PriceFilling": safe_decimal(price_filling),
    }
