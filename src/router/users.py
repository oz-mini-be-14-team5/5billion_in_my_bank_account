from fastapi import APIRouter, HTTPException, Depends
from datetime import date
from typing import List, Dict, DefaultDict
from collections import defaultdict
from tortoise.exceptions import DoesNotExist

from src.model.schema.token import (
    TokenRefreshRequest,
    TokenResponse,
)
import config
from src.model.schema.user import UserCreate, UserResponse, CalendarEntry
from src.model.users import User
from src.model.posts import Post
from fastapi.security import OAuth2PasswordRequestForm
from src.tools.jwt import get_current_user, create_access_token, create_refresh_token, decode_token
router = APIRouter(
    prefix="/api/v1/users",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user: User = await User.get(login_id=form_data.username)
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Invalid login ID or password")

    if not user.verify_password(form_data.password):
        raise HTTPException(status_code=400, detail="Invalid login ID or password")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in= config.jwt_access_min * 60,
        refresh_expires_in=config.jwt_refresh_day * 24 * 60 * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(request: TokenRefreshRequest):
    token_config = decode_token(request.refresh_token, expected_type="refresh")
    access_token = create_access_token(token_config.id, scopes=token_config.scopes)
    refresh_token = create_refresh_token(token_config.id, scopes=token_config.scopes)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=config.jwt_access_min * 60,
        refresh_expires_in=config.jwt_refresh_day * 24 * 60 * 60
    )

@router.post("/me", response_model=UserResponse)
async def get_user(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        username=user.username,
        number_of_posts=user.number_of_posts,
    )

@router.post("/", response_model=UserResponse)
async def create_user(user_create: UserCreate):
    if await User.filter(login_id=user_create.login_id).exists():
        raise HTTPException(status_code=400, detail="Login ID already registered")

    user = User(username=user_create.username, login_id=user_create.login_id)
    user.set_password(user_create.password)
    await user.save()
    return UserResponse(
        id=user.id,
        username=user.username,
        number_of_posts=user.number_of_posts,
    )

@router.get("/calender", response_model=List[CalendarEntry])
async def get_calender(user: User = Depends(get_current_user)):
    rows = (
        await Post.filter(author=user)
        .values_list("date", "id")
    )
    bucket: DefaultDict[date, List[int]] = defaultdict(list)
    for d, pid in rows:
        if pid not in bucket[d]:
            bucket[d].append(pid)
    return [CalendarEntry(date=d, post_ids=pids) for d, pids in bucket.items()]
