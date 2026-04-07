from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import select

from app.sources.openinsider import fetch
from app.db.engine import wait_for_db, SessionLocal, engine
from app.db.base import Base
from app.db.models import TradeRaw, TradeEnriched
from app.services.yahoo_enricher import enrich_trade
from app.services.stat_analyzer import run_analysis
from app.modules.extended.scraper import update_extended_module
from app.modules.extended.ticker_scraper import update_all_tickers


def job():
    print("Running scrape job...", flush=True)

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

        print(f"Inserted {inserted_raw} new raw trades", flush=True)
        print(f"Enriched {inserted_enriched} trades", flush=True)

    except Exception as e:
        print("ERROR:", e, flush=True)
        db.rollback()
    finally:
        db.close()

    print("Job finished.", flush=True)


def initial_full_pipeline():
    print("🔥 Running INITIAL FULL PIPELINE...", flush=True)

    job()
    update_all_tickers()
    update_extended_module()
    run_analysis()

    print("✅ INITIAL PIPELINE COMPLETED.", flush=True)


def main():
    print("Worker starting...", flush=True)

    wait_for_db()
    Base.metadata.create_all(bind=engine)

    # 🔥 FIRST RUN FULL SYSTEM
    initial_full_pipeline()

    scheduler = BlockingScheduler()

    # 🔁 Scrape + enrichment
    scheduler.add_job(job, "interval", minutes=1)

    # 🔁 Update tickers
    scheduler.add_job(
        update_all_tickers,
        trigger="interval",
        hours=12
    )

    # 🔁 Update extended history
    scheduler.add_job(
        update_extended_module,
        trigger="interval",
        hours=4
    )

    # 🔁 Run analysis regularly
    scheduler.add_job(
        run_analysis,
        trigger="interval",
        minutes=10
    )

    print("Scheduler started.", flush=True)

    scheduler.start()


if __name__ == "__main__":
    main()
