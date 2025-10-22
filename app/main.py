from contextlib import asynccontextmanager

from fastapi import FastAPI
"""
to run the server:

uvicorn app.main:app --host 0.0.0.0

"""

from app.db import Base, engine
from app.routes.api import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(user.route, prefix="/api/users", tags=["user"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}