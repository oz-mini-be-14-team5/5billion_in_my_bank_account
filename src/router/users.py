from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import DoesNotExist

from src.model.schema.token import (
    TokenRefreshRequest,
    TokenResponse,
)
import config
from src.model.schema.user import UserCreate, UserLogin, UserResponse
from src.model.users import User
from src.tools.jwt import get_current_user, create_access_token, create_refresh_token, decode_token
router = APIRouter(
    prefix="/api/v1/users",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login", response_model=TokenResponse)
async def login(user_login: UserLogin):
    try:
        user: User = await User.get(login_id=user_login.login_id)
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Invalid login ID or password")

    if not user.verify_password(user_login.password):
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
async def get_current_user(user: User = Depends(get_current_user)):
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
