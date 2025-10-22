from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from environs import Env
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_db
from app.models.user import User

env = Env()
env.read_env()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")
SECRET_KEY = env.str("JWT_SECRET_KEY")
JWT_ALGORITHM = env.str("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=120)
REFRESH_TOKEN_EXPIRE_MINUTES = env.int("REFRESH_TOKEN_EXPIRE_MINUTES", default=60 * 24 * 14)

class _TokenPayload(BaseModel):
    sub: str
    type: str
    scopes: List[str] = []
    exp: int

class _TokenConfig(BaseModel):
    user_id: int
    scopes: List[str]

def _create_token(*,user_id: int, scopes: Optional[List[str]] = None, minutes: int, token_type: str) -> str:
    to_encode = {
        "sub": str(user_id),
        "type": token_type,
        "scopes": scopes or [],
        "exp": datetime.now() + timedelta(minutes=minutes),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_access_token(user_id: int, scopes: Optional[List[str]] = None) -> str:
    return _create_token(
        user_id=user_id,
        scopes=scopes,
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        token_type="access",
    )

def create_refresh_token(user_id: int, scopes: Optional[List[str]] = None) -> str:
    return _create_token(
        user_id=user_id,
        scopes=scopes,
        minutes=REFRESH_TOKEN_EXPIRE_MINUTES,
        token_type="refresh",
    )

def _decode_token(token: str) -> _TokenPayload:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return _TokenPayload.model_validate(data)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def decode_token(token: str, expected_type: str) -> _TokenConfig:
    payload = _decode_token(token)
    if payload.type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    try:
        user_id = int(payload.sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _TokenConfig(user_id=user_id, scopes=payload.scopes)

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    token_config = decode_token(token, expected_type="access")
    result = await db.execute(
        select(User).where(User.id == token_config.user_id)
    )
    user = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
