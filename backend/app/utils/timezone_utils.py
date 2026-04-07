import pandas as pd
import pytz

US_EASTERN = pytz.timezone("US/Eastern")
UTC = pytz.utc


def filing_to_utc(filing_str: str):
    """
    Converts OpenInsider FilingDate (US/Eastern) → UTC aware datetime
    """

    dt = pd.to_datetime(filing_str)

    if dt.tzinfo is None:
        dt = US_EASTERN.localize(dt)

    return dt.astimezone(UTC)


def trade_date_to_utc(trade_date_str: str):
    """
    Converts TradeDate (YYYY-MM-DD) to UTC midnight
    """

    dt = pd.to_datetime(trade_date_str)

    if dt.tzinfo is None:
        dt = UTC.localize(dt)

    return dt
