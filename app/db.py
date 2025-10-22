from __future__ import annotations

from typing import AsyncGenerator

from environs import Env
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

env = Env()
env.read_env()

DATABASE_URL = env.str("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
ECHO_SQL = env.bool("DEBUG", False)

engine = create_async_engine(
    DATABASE_URL,
    echo=ECHO_SQL,
    future=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session