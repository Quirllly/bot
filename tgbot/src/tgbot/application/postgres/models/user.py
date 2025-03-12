from sqlalchemy import (
    Column,
    UUID,
    String,
    Boolean,
    Date,
    Integer,
    Float,
    text,
    TIMESTAMP,
    DateTime,
)
from sqlalchemy.orm import relationship
from .base import Base
from .user_task import user_task  # Import the association table, not the mapped class

class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    tg_id = Column(String, nullable=False, unique=True)
    username = Column(String)
    promo = Column(Boolean, nullable=False)
    daily_bonus = Column(Date, nullable=False)
    referrer = Column(UUID)
    referral_code = Column(String, nullable=False, unique=True)
    amount_of_referrals = Column(Integer, nullable=False, default=0)
    balance = Column(Float, nullable=False)
    earned = Column(Float, nullable=False)
    verify_timestamp = Column(TIMESTAMP)
    last_daily_bonus = Column(DateTime)
    last_click_timestamp = Column(
        TIMESTAMP, server_default=text("'2001-01-01 01:00:00'")
    )
    boost_timestamp = Column(
        TIMESTAMP, server_default=text("'2001-01-01 01:00:00'")
    )

    subscriptions = relationship(
        "Subscription", back_populates="user"
    )

    tasks = relationship(
        "Task",
        secondary=user_task,  # Use the association table here
        back_populates="users",
        passive_deletes=True,
    )
    promocodes = relationship(
        'Promocode', 
        secondary='user_promocodes', 
        back_populates='users',
        cascade='all, delete'
    )