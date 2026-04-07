import requests
from sqlalchemy import select
from app.db.engine import SessionLocal
from app.db.models import Ticker


def save_ticker(symbol, name, exchange):
    if not symbol:
        return

    symbol = symbol.strip()

    # 🔥 FILTR BEZPIECZEŃSTWA
    if len(symbol) > 15:
        return

    # tylko litery, cyfry, . - /
    import re
    if not re.match(r"^[A-Z0-9.\-\/]+$", symbol):
        return

    db = SessionLocal()

    try:
        existing = db.execute(
            select(Ticker).where(Ticker.symbol == symbol)
        ).scalar_one_or_none()

        if existing:
            return

        ticker = Ticker(
            symbol=symbol,
            name=name.strip()[:400] if name else "",
            exchange=exchange,
            isNYSEorNASDAQ=exchange in ["NYSE", "NASDAQ"]
        )

        db.add(ticker)
        db.commit()

    except Exception as e:
        db.rollback()
        print("Ticker DB error:", e)

    finally:
        db.close()


# -----------------------------------------
# NYSE
# -----------------------------------------
def fetch_nyse():
    url = "https://datahub.io/core/nyse-other-listings/r/nyse-listed.csv"
    print("📥 Fetching NYSE...")

    r = requests.get(url, timeout=30)
    r.raise_for_status()

    lines = r.text.splitlines()
    headers = lines[0].split(",")

    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) < 2:
            continue

        symbol = parts[0]
        name = parts[1]

        save_ticker(symbol, name, "NYSE")


# -----------------------------------------
# NASDAQ
# -----------------------------------------
def fetch_nasdaq():
    url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
    print("📥 Fetching NASDAQ...")

    r = requests.get(url, timeout=30)
    r.raise_for_status()

    for line in r.text.splitlines():
        if "|" not in line:
            continue

        parts = line.split("|")

        if parts[0] == "Symbol":
            continue

        symbol = parts[0]
        name = parts[1]

        save_ticker(symbol, name, "NASDAQ")


# -----------------------------------------
# OTHER LISTED
# -----------------------------------------
def fetch_other():
    url = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
    print("📥 Fetching OTHER LISTED...")

    r = requests.get(url, timeout=30)
    r.raise_for_status()

    for line in r.text.splitlines():
        if "|" not in line:
            continue

        parts = line.split("|")

        if parts[0] == "ACT Symbol":
            continue

        symbol = parts[0]
        name = parts[1]

        save_ticker(symbol, name, "OTHER")


def update_all_tickers():
    print("🔵 Updating tickers table...")

    fetch_nyse()
    fetch_nasdaq()
    fetch_other()

    print("✅ Tickers updated.")
