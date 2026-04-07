import time

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import select, func

from app.sources.openinsider import fetch
from app.db.engine import wait_for_db, SessionLocal, engine
from app.db.base import Base
from app.db.models import TradeRaw, TradeEnriched
from app.services.yahoo_enricher import enrich_trade
from app.services.stat_analyzer import run_analysis

from app.modules.extended.models_extended import InsiderExtended


def scrape_and_enrich():
    print("🔵 CORE: Running scrape + enrichment...", flush=True)

    db = SessionLocal()

    try:
        data = fetch()
        print(f"Fetched {len(data)} records", flush=True)

        inserted_raw = 0
        inserted_enriched = 0

        for record in data:

            existing_raw = db.execute(
                select(TradeRaw).where(
                    TradeRaw.trade_hash == record["hash"]
                )
            ).scalar_one_or_none()

            if existing_raw:
                continue

            trade = TradeRaw(
                source="openinsider",
                trade_hash=record["hash"],
                payload=record
            )

            db.add(trade)
            db.flush()

            inserted_raw += 1

            enriched_data = enrich_trade(trade)

            if enriched_data:
                enriched = TradeEnriched(
                    trade_id=trade.id,
                    **enriched_data
                )
                db.add(enriched)
                inserted_enriched += 1

        db.commit()

        print(f"Inserted RAW: {inserted_raw}", flush=True)
        print(f"Enriched: {inserted_enriched}", flush=True)

    except Exception as e:
        print("CORE ERROR:", e, flush=True)
        db.rollback()
    finally:
        db.close()

    print("CORE job finished.", flush=True)

def wait_for_extended_ready():
    db = SessionLocal()
    try:
        count = db.execute(
            select(func.count()).select_from(InsiderExtended)
        ).scalar()

        if count < 50:
            print("⏳ Waiting for extended data...")
            time.sleep(10)
            return False

        return True
    finally:
        db.close()
def initial_core_pipeline():
    print("🔥 CORE: Initial pipeline start...")

    scrape_and_enrich()

    while True:
        if wait_for_extended_ready():
            break
        time.sleep(5)

    run_analysis()

    print("🔥 CORE: Initial pipeline done.")


def main():
    print("🚀 CORE Worker starting...", flush=True)

    wait_for_db()
    Base.metadata.create_all(bind=engine)

    initial_core_pipeline()

    scheduler = BlockingScheduler()

    scheduler.add_job(scrape_and_enrich, "interval", minutes=1)

    scheduler.add_job(run_analysis, "interval", minutes=5)

    print("CORE Scheduler started.", flush=True)

    scheduler.start()


if __name__ == "__main__":
    main()
