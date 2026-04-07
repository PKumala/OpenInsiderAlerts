import time
import random
import hashlib
import requests
from bs4 import BeautifulSoup

URL = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=3000&page=1"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

HTTP = requests.Session()
HTTP.headers.update(HEADERS)


def parse_value(val: str) -> float:
    try:
        val = val.strip()
        negative = "(" in val and ")" in val
        val = val.replace("$", "").replace(",", "").replace("+", "")
        val = val.replace("(", "").replace(")", "")
        num = float(val)
        return -num if negative else num
    except Exception:
        return 0.0


def generate_hash(record: dict) -> str:
    raw = f"{record['FilingDate']}_{record['TradeDate']}_{record['Ticker']}_{record['Insider']}_{record['PriceReported']}"
    return hashlib.sha256(raw.encode()).hexdigest()


def fetch(retries: int = 5, pause: float = 1.5) -> list[dict]:

    for attempt in range(1, retries + 1):
        try:
            r = HTTP.get(URL, timeout=20)
            r.raise_for_status()
        except requests.RequestException:
            time.sleep(pause * attempt + random.uniform(0, 0.5))
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.select_one("table.tinytable")

        if not table:
            time.sleep(pause * attempt)
            continue

        data = []

        for tr in table.select("tr"):
            if tr.find("th"):
                continue

            tds = tr.find_all("td")
            if len(tds) < 9:
                continue

            cols = [td.get_text(strip=True) for td in tds]

            record = {
                "FilingDate": cols[1],
                "TradeDate": cols[2],
                "Ticker": cols[3],
                "Company": cols[4],
                "Insider": cols[5],
                "Title": cols[6],
                "TradeType": cols[7],
                "PriceReported": cols[8],
                "Value": parse_value(cols[12]) if len(cols) > 12 else 0.0,
            }

            record["hash"] = generate_hash(record)

            data.append(record)

        return data

    return []
