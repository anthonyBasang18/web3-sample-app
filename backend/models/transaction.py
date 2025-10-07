from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String, unique=True, index=True)
    from_address = Column(String, index=True)
    to_address = Column(String, index=True)
    value = Column(String)
    asset = Column(String, default="ETH")
    block_number = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
