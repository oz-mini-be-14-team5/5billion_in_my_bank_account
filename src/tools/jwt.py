from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from src.model.users import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

class _TokenPayload(BaseModel):
    sub: str
    type: str
    scopes: List[str] = []
    exp: int

class _TokenConfig(BaseModel):
    id: int
    scopes: List[str]

def _create_token(*, id: int, scopes: Optional[List[str]] = None, minutes: int, token_type: str) -> str:
    to_encode = {
        "sub": str(id),
        "type": token_type,
        "scopes": scopes or [],
        "exp": datetime.now() + timedelta(minutes=minutes),
    }
    return jwt.encode(to_encode, config.jwt_secret_key, algorithm=config.jwt_algorithm)

def create_access_token(id: int, scopes: Optional[List[str]] = None) -> str:
    return _create_token(
        id=id,
        scopes=scopes,
        minutes=config.jwt_access_min,
        token_type="access",
    )

def create_refresh_token(id:int, scopes: Optional[List[str]] = None) -> str:
    return _create_token(
        id=id,
        scopes=scopes,
        minutes=config.jwt_refresh_day * 24 * 60,
        token_type="refresh",
    )

def decode_token(token: str, expected_type: str) -> _TokenConfig:
    payload: _TokenPayload
    try:
        payload =  jwt.decode(token, config.jwt_secret_key, algorithms=[config.jwt_algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
    return _TokenConfig(id=user_id, scopes=payload.scopes)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    token_config = decode_token(token, expected_type="access")
    result = await User.filter(id=token_config.id).first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result
