from sqlalchemy import (
    String,
    Boolean,
    Integer,
    Text,
    JSON,
    DateTime,
    BigInteger,
    func, Float, ForeignKey,
)
from sqlalchemy.orm import mapped_column, Mapped
from app.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
# -------------------------
# RAW TRADES (SCRAPE)
# -------------------------

class TradeRaw(Base):
    __tablename__ = "trades_raw"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    trade_hash = Column(String, unique=True, index=True)
    payload = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    enriched = relationship("TradeEnriched", back_populates="trade", uselist=False)

# -------------------------
# ENRICHED TRADES
# -------------------------

class TradeEnriched(Base):
    __tablename__ = "trades_enriched"

    id = Column(Integer, primary_key=True)
    trade_id = Column(Integer, ForeignKey("trades_raw.id"), unique=True)

    # ======= CORE DATA =======
    Ticker = Column(String(20))
    Insider = Column(String(200))
    FilingDate = Column(DateTime)
    TradeDate = Column(DateTime)

    # ======= YAHOO DATA =======
    PriceReported = Column(Numeric(15, 4))
    LowTradeDay = Column(Numeric(15, 4))
    HighTradeDay = Column(Numeric(15, 4))
    TickerAgeDays = Column(Integer)
    OHLCJson = Column(JSON)
    Value = Column(Numeric(20, 4))
    Price = Column(Numeric(20, 4))
    PriceFilling = Column(Numeric(15, 4))

    enriched_at = Column(DateTime(timezone=True), server_default=func.now())

    trade = relationship("TradeRaw", back_populates="enriched")



# -------------------------
# FILTERS
# -------------------------

class Filter(Base):
    __tablename__ = "filters"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100))
    type = mapped_column(String(100))
    params = mapped_column(JSON)
    enabled = mapped_column(Boolean, default=True)
    position = mapped_column(Integer)

# -------------------------
# ALERT LOG
# -------------------------

class AlertLog(Base):
    __tablename__ = "alerts_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    trade_hash: Mapped[str] = mapped_column(String(128))
    payload: Mapped[dict] = mapped_column(JSON)

    sent_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
class AnalyzedTrade(Base):
    __tablename__ = "analyzed_trades"

    id = Column(Integer, primary_key=True)

    FilingDate = Column(DateTime)
    TradeDate = Column(DateTime)
    Ticker = Column(String(20))

    PriceReported = Column(Numeric(15, 4))
    LowTradeDay = Column(Numeric(15, 4))
    HighTradeDay = Column(Numeric(15, 4))

    # Price analytics
    DiffAbove = Column(Numeric(10, 4))
    DiffBelow = Column(Numeric(10, 4))
    InsidePos = Column(Numeric(10, 4))
    InsideCat = Column(String(50))

    BusinessDaysDiff = Column(Integer)
    BusinessDaysCat = Column(String(20))

    ClusterNo = Column(Integer)
    ClusterRate = Column(String(5))
    DiffRate = Column(String(5))
    DiffAboveCat = Column(String(50))
    DiffBelowCat = Column(String(50))

    Value = Column(Numeric(20, 4))
    PriceFillingReported = Column(Numeric(15, 4))
    # 🔥 Nowe kolumny inteligentne
    IsFirstTrade = Column(Boolean)
    IsLastTrade = Column(Boolean)
    IsLastSale = Column(Boolean)
    IsNYSEorNASDAQ = Column(Boolean)
    NotDir = Column(Boolean)
    TickerAgeDays = Column(Integer)
class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True)

    symbol = Column(String(30), unique=True, index=True)
    name = Column(String(500))
    exchange = Column(String(20))

    isNYSEorNASDAQ = Column(Boolean, default=False)
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    analyzed_id = Column(Integer, ForeignKey("analyzed_trades.id"), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
