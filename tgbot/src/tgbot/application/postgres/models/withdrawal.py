from sqlalchemy import Column, UUID, Float, String, DateTime, ForeignKey,text
from datetime import datetime
from .base import Base

class WithdrawalRequest(Base):
    __tablename__ = "withdrawl_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    dd = Column(String(50), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,unique=False )
    amount = Column(Float, nullable=False)
    gift_type = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')  # pending/approved/rejected
    created_at = Column(DateTime, default=datetime.utcnow)