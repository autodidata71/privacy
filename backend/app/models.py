from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from .database import Base
import enum


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class FinanceType(str, enum.Enum):
    income = "income"
    expense = "expense"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default="medium")
    category = Column(String(100), default="geral")
    status = Column(String(30), default="pending")
    due_date = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), default="geral")
    tags = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Finance(Base):
    __tablename__ = "finances"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)
    category = Column(String(100), default="outros")
    date = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
