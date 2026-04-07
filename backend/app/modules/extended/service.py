from app.modules.extended.scraper import fetch_extended_for_ticker
from app.modules.extended.models_extended import InsiderExtended
from app.db.engine import SessionLocal


def update_extended_data(ticker, trade_date):
    db = SessionLocal()

    try:
        data = fetch_extended_for_ticker(ticker)

        record = InsiderExtended(
            Ticker=ticker,
            TradeDate=trade_date,
            IsFirstTradeEver=data["IsFirstTradeEver"],
            IsLastSaleEver=data["IsLastSaleEver"],
            Exchange=data["Exchange"],
            IsNYSEorNASDAQ=data["IsNYSEorNASDAQ"],
            SourceDatabase="external_v1"
        )

        db.add(record)
        db.commit()

    finally:
        db.close()
