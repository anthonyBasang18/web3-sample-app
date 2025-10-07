from sqlalchemy import Column, String, DateTime, Numeric
from datetime import datetime
from database import Base

class AccountBalance(Base):
    __tablename__ = "account_balances"
    
    address = Column(String, primary_key=True, index=True)
    balance_wei = Column(String, nullable=False)
    balance_eth = Column(Numeric(precision=30, scale=18), nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
