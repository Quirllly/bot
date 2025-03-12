from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class UserPromocode(Base):
    __tablename__ = 'user_promocodes'
    
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
    promocode_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('promocodes.id', ondelete='CASCADE'),
        primary_key=True
    )