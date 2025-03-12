from sqlalchemy import Column, UUID, ForeignKey, TIMESTAMP, Boolean, text
from sqlalchemy.orm import relationship
from .base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    user_id = Column(
        UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    sponsor_id = Column(
        UUID, ForeignKey("sponsors.id", ondelete="CASCADE"), nullable=False
    )
    subscribed_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    is_active = Column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="subscriptions")
    sponsor = relationship("Sponsor", back_populates="subscriptions")
