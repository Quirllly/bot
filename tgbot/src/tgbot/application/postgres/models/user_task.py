from sqlalchemy import Column, ForeignKey, Table, UUID, JSON, Integer
from .base import Base
from sqlalchemy.ext.mutable import MutableList
# Таблица для связи многие-ко-многим между User и Task
user_task = Table(
    "user_task",
    Base.metadata,
    Column(
        "user_id", 
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "task_id", 
        Integer, 
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True
    )
)

# Отдельная модель для хранения дополнительных данных
class UserTaskData(Base):
    __tablename__ = "user_task_data"
    
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        primary_key=True
    )
    used_invites = Column(JSON, default=dict)  # Храним использованные инвайты
    started_bots = Column(JSON, default=list)  # Храним запущенных ботов
    completed_tasks = Column(MutableList.as_mutable(JSON), default=[])