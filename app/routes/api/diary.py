from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth import get_current_user
from app.db import get_db
from app.models.diary import CreateDiary, Diary
from app.models.user import User

route = APIRouter()


@route.post("/", status_code=status.HTTP_201_CREATED)
async def post_diary(
    diary: CreateDiary,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    contents_html: UploadFile = File(...),
):
    existing_diary = await db.execute(
        select(Diary).where(
            Diary._date == diary._date,
            Diary.author_id == current_user.id
        )
    )
    if existing_diary.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="already a diary entry for that date",
        )

    storage_key = f"{uuid4()}_{contents_html.filename}"

    new_diary = Diary(
        **diary.model_dump(),
        author=current_user,
        content_url=storage_key,
    )
    db.add(new_diary)
    await db.commit()
    await db.refresh(new_diary)
    return {
        "detail": "Diary created",
        "diary_id": new_diary.id,
        "content_url": new_diary.content_url,
    }
