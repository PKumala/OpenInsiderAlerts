import requests
import random
import time
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy import select
from app.db.engine import SessionLocal
from app.modules.extended.models_extended import InsiderExtended
from app.db.models import Ticker

BASE_URL = (
    "http://openinsider.com/screener?"
    "s={symbol}&o=&pl=&ph=&ll=&lh=&fd=1461&fdr=&td=0&tdr=&"
    "xp=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&"
    "nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&"
    "sortcol=0&cnt=1000&page=1"
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]


def clean_price(x):
    if not x:
        return None
    x = x.replace("$", "").replace(",", "")
    try:
        return float(x)
    except:
        return None


def parse_datetime(dt_str):
    if not dt_str:
        return None
    dt_str = dt_str.strip()
    try:
        if len(dt_str) > 10:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return datetime.strptime(dt_str, "%Y-%m-%d")
    except:
        return None


def get_all_tickers():
    db = SessionLocal()
    try:
        tickers = db.execute(select(Ticker)).scalars().all()
        return tickers
    finally:
        db.close()


def scrape_symbol(symbol):
    url = BASE_URL.format(symbol=symbol)

    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }

    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.select_one("table.tinytable")

    if not table:
        return []

    rows = []

    for tr in table.select("tr")[1:]:
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cols) < 13:
            continue

        record = {
            "FilingDate": parse_datetime(cols[1]),
            "TradeDate": parse_datetime(cols[2]),
            "Ticker": cols[3],
            "Insider": cols[4],  # Zmienione z 5
            "Title": cols[5],  # Zmienione z 6
            "TradeType": cols[6],  # Zmienione z 7
            "PriceReported": clean_price(cols[7]),  # Zmienione z 8
            "Value": clean_price(cols[11]),  # Zmienione z 12
        }

        rows.append(record)

    return rows


def compute_flags(records):
    if not records:
        return records

    # sort per ticker
    records = sorted(records, key=lambda x: x["TradeDate"] or datetime.min)

    first_date = records[0]["TradeDate"]
    last_sale_date = None

    for r in records:
        if r["TradeType"] and r["TradeType"].startswith("S"):
            last_sale_date = r["TradeDate"]

    for r in records:
        r["IsFirstTradeEver"] = r["TradeDate"] == first_date
        r["IsLastSaleEver"] = (
            last_sale_date is not None and r["TradeDate"] == last_sale_date
        )

    return records


def update_extended_module():
    print("🔵 EXTENDED MODULE START")

    tickers = get_all_tickers()

    db = SessionLocal()

    try:
        for ticker in tickers:
            print(f"Scraping {ticker.symbol}")

            try:
                records = scrape_symbol(ticker.symbol)

                if not records:
                    continue

                records = compute_flags(records)

                for r in records:
                    exists = db.query(InsiderExtended).filter(
                        InsiderExtended.Ticker == r["Ticker"],
                        InsiderExtended.TradeDate == r["TradeDate"],
                        InsiderExtended.Insider == r["Insider"]
                    ).first()

                    if exists:
                        continue

                    new = InsiderExtended(
                        FilingDate=r["FilingDate"],
                        TradeDate=r["TradeDate"],
                        Ticker=r["Ticker"],
                        Insider=r["Insider"],
                        Title=r["Title"],
                        TradeType=r["TradeType"],
                        PriceReported=r["PriceReported"],
                        Value=r["Value"],
                        IsFirstTradeEver=r["IsFirstTradeEver"],
                        IsLastSaleEver=r["IsLastSaleEver"],
                        IsNYSEorNASDAQ=(ticker.exchange in ["NYSE", "NASDAQ"]),
                        Exchange=ticker.exchange
                    )

                    db.add(new)

                db.commit()

                # delikatne opóźnienie
                time.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                print("ERROR:", e)

    finally:
        db.close()

    print("🟢 EXTENDED MODULE DONE")
