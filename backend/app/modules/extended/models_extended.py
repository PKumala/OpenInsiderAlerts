from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric
from app.db.base import Base

class InsiderExtended(Base):
    __tablename__ = "insider_extended"

    id = Column(Integer, primary_key=True)

    FilingDate = Column(DateTime)
    TradeDate = Column(DateTime)
    Ticker = Column(String(20))

    Insider = Column(String(255))
    Title = Column(String(255))
    TradeType = Column(String(20))

    PriceReported = Column(Numeric(15,4))
    Value = Column(Numeric(20,4))

    IsFirstTradeEver = Column(Boolean)
    IsLastSaleEver = Column(Boolean)
    IsNYSEorNASDAQ = Column(Boolean)

    Exchange = Column(String(20))