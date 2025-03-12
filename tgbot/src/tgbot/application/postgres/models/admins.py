from sqlalchemy import Column, BigInteger, DateTime, Boolean
from datetime import datetime
from .base import Base
class Admins(Base):
    __tablename__ = "admins"

    user_id = Column(BigInteger, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_superadmin = Column(Boolean, default=False)