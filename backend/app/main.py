from fastapi import FastAPI
from app.db.base import Base
from app.db.engine import engine, wait_for_db
from app.api.routes import filters
from app.api.routes import alerts
from app.api.routes import filters_meta
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
def startup():
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    app.include_router(filters.router)
    app.include_router(filters_meta.router)
    app.include_router(alerts.router)

