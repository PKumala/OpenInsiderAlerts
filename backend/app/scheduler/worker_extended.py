from apscheduler.schedulers.blocking import BlockingScheduler

from app.db.engine import wait_for_db, engine
from app.db.base import Base
from app.modules.extended.scraper import update_extended_module
from app.modules.extended.ticker_scraper import update_all_tickers


def extended_job():
    print("🟢 EXTENDED: Updating tickers + extended history...", flush=True)

    try:
        update_all_tickers()
        update_extended_module()
    except Exception as e:
        print("EXTENDED ERROR:", e, flush=True)

    print("EXTENDED job finished.", flush=True)


def initial_extended_pipeline():
    print("🔥 EXTENDED: Initial pipeline start...", flush=True)

    extended_job()

    print("🔥 EXTENDED: Initial pipeline done.", flush=True)


def main():
    print("🚀 EXTENDED Worker starting...", flush=True)

    wait_for_db()
    Base.metadata.create_all(bind=engine)

    initial_extended_pipeline()

    scheduler = BlockingScheduler()

    scheduler.add_job(extended_job, "interval", hours=4)

    print("EXTENDED Scheduler started.", flush=True)

    scheduler.start()


if __name__ == "__main__":
    main()
