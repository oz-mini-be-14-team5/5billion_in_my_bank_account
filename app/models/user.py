from __future__ import annotations

from datetime import datetime


from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, Integer, Numeric, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

from .diary import Diary

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    login_id: Mapped[str] = mapped_column(String(32), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    articles: Mapped[list[Diary]] = relationship(back_populates="author")
    join_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class UserCreate(BaseModel):
    name: str
    login_id: str
    password: str

class UserLogin(BaseModel):
    login_id: str
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    articles: list[int] = Field(default_factory=list)
    join_date: datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int
    user: UserOut

class TokenRefreshRequest(BaseModel):
    refresh_token: str
