from .base import Base

from sqlalchemy import Column, text, String, UUID
from sqlalchemy.dialects.postgresql import JSONB


class Metadata(Base):
    __tablename__ = "metadata"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    name = Column(String, nullable=False, unique=True)
    data = Column(JSONB, nullable=False)
