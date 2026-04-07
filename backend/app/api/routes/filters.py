from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.engine import SessionLocal
from app.db.models import Filter

router = APIRouter(prefix="/filters", tags=["Filters"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_filters(db: Session = Depends(get_db)):
    return db.execute(select(Filter).order_by(Filter.position)).scalars().all()


@router.post("/")
def create_filter(data: dict, db: Session = Depends(get_db)):

    new_filter = Filter(
        name=data["name"],
        type=data["type"],
        params=data.get("params", {}),
        enabled=data.get("enabled", True),
        position=data.get("position", 0),
    )

    db.add(new_filter)
    db.commit()
    db.refresh(new_filter)

    return new_filter


@router.put("/{filter_id}")
def update_filter(filter_id: int, data: dict, db: Session = Depends(get_db)):

    f = db.get(Filter, filter_id)

    if not f:
        raise HTTPException(status_code=404)

    f.name = data.get("name", f.name)
    f.type = data.get("type", f.type)
    f.params = data.get("params", f.params)
    f.enabled = data.get("enabled", f.enabled)
    f.position = data.get("position", f.position)

    db.commit()

    return f


@router.delete("/{filter_id}")
def delete_filter(filter_id: int, db: Session = Depends(get_db)):

    f = db.get(Filter, filter_id)

    if not f:
        raise HTTPException(status_code=404)

    db.delete(f)
    db.commit()

    return {"status": "deleted"}