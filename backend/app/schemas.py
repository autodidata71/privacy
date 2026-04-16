from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    category: str = "geral"
    status: str = "pending"
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    category: str
    status: str
    due_date: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    title: str
    content: str
    category: str = "geral"
    tags: Optional[str] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None


class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class FinanceCreate(BaseModel):
    description: str
    amount: float
    type: str
    category: str = "outros"
    date: str


class FinanceOut(BaseModel):
    id: int
    description: str
    amount: float
    type: str
    category: str
    date: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
