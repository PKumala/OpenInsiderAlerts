from sqlalchemy import select
from app.db.engine import SessionLocal
from app.db.models import Filter
from app.modules.filters.registry import FILTER_REGISTRY


def run_filters(trade) -> bool:
    """
    AND logic:
    Wszystkie filtry muszą przejść
    """

    db = SessionLocal()

    try:
        filters = db.execute(
            select(Filter)
            .where(Filter.enabled == True)
            .order_by(Filter.position)
        ).scalars().all()

        for f in filters:

            filter_class = FILTER_REGISTRY.get(f.type)

            if not filter_class:
                continue

            instance = filter_class(f.params)

            if not instance.check(trade):
                return False

        return True

    finally:
        db.close()