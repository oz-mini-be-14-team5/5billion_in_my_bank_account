from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from environs import Env

from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.db import get_db
from app.models.user import (
    PasswordChange,
    UserCreate,
    TokenResponse,
    TokenRefreshRequest,
    User,
    UserLogin,
    UserOut,
)
from app.models.diary import CreateDiary , Diary

env = Env()
env.read_env()

route = APIRouter()

@route.post("/", response_model=TokenResponse)
async def post_diary(diary: CreateDiary,
                     db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     contents_html: UploadFile = File(...)
                     ):
    result =  await db.execute(select(Diary).where(Diary._date == diary._date and Diary.author == current_user.id))
    db_except = result.scalars().first()
    if db_except:
        raise HTTPException(400,detail="already a diary entry for that date")
    else:
        # contents_html 이름 재작성 , storage에 보관
        new_diary = Diary(**diary.model_dump(),
                          author=current_user.id
                          )
        # new_diary.content_url 에 저장된 위치 기록