from sqlalchemy import Column, Integer, JSON, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import text
from enum import Enum
from datetime import datetime
from .base import Base
from sqlalchemy.orm import relationship
from .user_task import user_task  # Import the association table

# Исправленный ENUM
class TaskType(str, Enum):
    SUBSCRIPTION = "subscription"
    INVITE_LINK = "invite_link"
    BOT_START = "bot_start"

# Создаем ENUM с явным указанием значений
task_type_enum = ENUM(
    *[member.value for member in TaskType],  # Получаем значения из Enum
    name="tasktype",
    create_type=True,
    validate_strings=True
)

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    type = Column(task_type_enum, nullable=False)
    title = Column(String(100))
    description = Column(Text)
    reward = Column(Float, nullable=False)
    channel_id = Column(String)
    invite_link = Column(String)
    chat_id = Column(String)
    bot_username = Column(String)
    bot_token = Column(String)
    giphy_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship(
        "User",
        secondary=user_task,  # Use the association table here
        back_populates="tasks"
    )