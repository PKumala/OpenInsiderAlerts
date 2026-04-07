from sqlalchemy import select, func
from app.db.engine import SessionLocal
from app.db.models import TradeEnriched, Ticker, AnalyzedTrade
from app.modules.extended.models_extended import InsiderExtended
import numpy as np
from app.modules.filters.engine import run_filters
from app.db.models import Alert

def compute_price_position(price, low, high):

    if price is None or low is None or high is None:
        return None, None, None, None

    if high == low:
        return 0, 0, 0.5, "Inside-Mid"

    diff_above = ((price - high) / high) * 100 if high else 0
    diff_below = ((price - low) / low) * 100 if low else 0
    spread_position = (price - low) / (high - low)

    spread_position = min(max(spread_position, 0), 1)

    if spread_position < 0.25:
        cat = "Inside-Low"
    elif spread_position < 0.75:
        cat = "Inside-Mid"
    else:
        cat = "Inside-High"

    return diff_above, diff_below, spread_position, cat


def categorize_diff(x):
    if x is None:
        return None

    if x == 0:
        return "0"

    if x > 0:
        if x <= 2:
            return "Above 0-2%"
        elif x <= 5:
            return "Above 2-5%"
        elif x <= 10:
            return "Above 5-10%"
        else:
            return "Above 10%+"
    else:
        ax = abs(x)
        if ax <= 2:
            return "Below 0-2%"
        elif ax <= 5:
            return "Below 2-5%"
        elif ax <= 10:
            return "Below 5-10%"
        else:
            return "Below 10%+"


def run_analysis():

    print("📊 Running FULL statistical analysis...")

    db = SessionLocal()

    try:
        existing_ids = db.execute(
            select(AnalyzedTrade.Ticker, AnalyzedTrade.TradeDate)
        ).all()

        existing_set = {(e[0], e[1]) for e in existing_ids}

        enriched_trades = db.execute(select(TradeEnriched)).scalars().all()

        enriched_trades = [
            t for t in enriched_trades
            if (t.Ticker, t.TradeDate) not in existing_set
        ]

        for trade in enriched_trades:

            extended = db.execute(
                select(InsiderExtended).where(
                    InsiderExtended.Ticker == trade.Ticker,
                    func.date(InsiderExtended.TradeDate) == func.date(trade.TradeDate),
                    InsiderExtended.Insider == trade.Insider
                )
            ).scalars().first()

            ticker = db.execute(
                select(Ticker).where(Ticker.symbol == trade.Ticker)
            ).scalar_one_or_none()

            price = float(trade.PriceReported or 0)
            low = float(trade.LowTradeDay or 0)
            high = float(trade.HighTradeDay or 0)

            diff_above, diff_below, inside_pos, inside_cat = compute_price_position(
                price, low, high
            )

            diff_above_cat = categorize_diff(diff_above)
            diff_below_cat = categorize_diff(diff_below)

            # ------------------------
            # Business Days
            # ------------------------

            if trade.FilingDate and trade.TradeDate:
                business_days = (trade.FilingDate - trade.TradeDate).days
            else:
                business_days = None

            if business_days is None:
                business_rate = None
            elif business_days == 0:
                business_rate = "A"
            elif business_days == 1:
                business_rate = "B"
            else:
                business_rate = "C"

            # ------------------------
            # Cluster Rate
            # ------------------------

            cluster_no = 1
            cluster_rate = "B"

            if extended and extended.IsFirstTradeEver:
                cluster_no = 1
                cluster_rate = "A"

            # ------------------------
            # Diff Rate
            # ------------------------

            if diff_above == 0 and diff_below == 0:
                diff_rate = "A"
            else:
                diff_rate = "B"

            analyzed = AnalyzedTrade(
                FilingDate=trade.FilingDate,
                TradeDate=trade.TradeDate,
                Ticker=trade.Ticker,
                PriceReported=price,
                LowTradeDay=low,
                HighTradeDay=high,
                DiffAbove=diff_above,
                DiffBelow=diff_below,
                InsidePos=inside_pos,
                InsideCat=inside_cat,
                BusinessDaysDiff=business_days,
                BusinessDaysCat=business_rate,
                ClusterNo=cluster_no,
                ClusterRate=cluster_rate,
                DiffRate=diff_rate,
                DiffAboveCat=diff_above_cat,
                DiffBelowCat=diff_below_cat,
                Value=trade.Value,
                PriceFillingReported=trade.PriceFilling,  # 🔥 KLUCZOWE
                IsFirstTrade=extended.IsFirstTradeEver if extended else False,
                IsLastTrade=False,  # 🔥 BRAKOWAŁO TEGO POLA
                IsLastSale=extended.IsLastSaleEver if extended else False,
                IsNYSEorNASDAQ=ticker.isNYSEorNASDAQ if ticker else False,
                NotDir=(extended.Title != "Dir") if extended else False,
                TickerAgeDays=trade.TickerAgeDays
            )

            db.add(analyzed)
            db.flush()
            if run_filters(analyzed):

                # sprawdź czy alert już istnieje
                existing_alert = db.query(Alert).filter(
                    Alert.analyzed_id == analyzed.id
                ).first()

                if not existing_alert:
                    alert = Alert(analyzed_id=analyzed.id)
                    db.add(alert)
        db.commit()

        print("✅ FULL analysis completed.")

    finally:
        db.close()
