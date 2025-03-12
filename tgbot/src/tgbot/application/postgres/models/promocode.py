from .base import Base
import enum

from datetime import datetime
from sqlalchemy import Column, DateTime, Enum
from sqlalchemy import UUID, String, text, Float, Integer
from sqlalchemy.orm import relationship
class PromocodeType(enum.Enum):
    simple = "simple"
    referral_based = "referral_based"

class Promocode(Base):
    __tablename__ = "promocodes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    name = Column(String, nullable=False, unique=True)
    type = Column(Enum(PromocodeType), nullable=False)
    reward = Column(Float, nullable=False)
    required_referrals = Column(Integer, default=0) 
    remaining_usages = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    users = relationship(
        'User', 
        secondary='user_promocodes', 
        back_populates='promocodes',
        cascade='all, delete'
    )
