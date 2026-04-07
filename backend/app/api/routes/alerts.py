from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.engine import SessionLocal
from app.db.models import Alert

from app.db.models import Alert, AnalyzedTrade
router = APIRouter(prefix="/alerts", tags=["Alerts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_alerts(db: Session = Depends(get_db)):

    results = db.execute(
        select(Alert, AnalyzedTrade)
        .join(AnalyzedTrade, Alert.analyzed_id == AnalyzedTrade.id)
        .order_by(Alert.id.desc())
    ).all()

    response = []

    for alert, trade in results:
        response.append({
            "alert_id": alert.id,
            "triggered_at": alert.created_at,
            "ticker": trade.Ticker,
            "filing_date": trade.FilingDate,
            "trade_date": trade.TradeDate,
            "price_filling": trade.PriceFillingReported
        })

    return response
@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):

    alert = db.get(Alert, alert_id)

    if not alert:
        return {"error": "Not found"}

    db.delete(alert)
    db.commit()

    return {"status": "deleted"}
@router.delete("/")
def delete_all_alerts(db: Session = Depends(get_db)):

    db.query(Alert).delete()
    db.commit()

    return {"status": "all deleted"}