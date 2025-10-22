from __future__ import annotations

from datetime import datetime
from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, Integer, Numeric, String, TIMESTAMP, func, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .user import User

class Diary(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    content_url: Mapped[str] = mapped_column(String(255), unique=True)
    author: Mapped[User] = relationship(back_populates="articles")
    _date: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

class CreateDiary(BaseModel):
    title: str
    _date: date