from fastapi import APIRouter, Depends, HTTPException, status
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

env = Env()
env.read_env()

PASSWORD_SALT = env.str("PASSWORD_SALT", default="")
PASSWORD_SECRET = env.str("PASSWORD_SECRET",default="NOT_SET")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

route = APIRouter()


async def _build_user_output(user: User, db: AsyncSession) -> UserOut:
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await db.refresh(user, attribute_names=["articles"])
    article_ids = [article.id for article in user.articles]
    return UserOut(
        name=user.name,
        articles=article_ids,
        join_date=user.join_date,
    )


def hash_password(password: str) -> str:
    token = f"{password}{PASSWORD_SALT}{PASSWORD_SECRET}"
    return pwd_context.hash(token)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    token = f"{plain_password}{PASSWORD_SALT}{PASSWORD_SECRET}"
    return pwd_context.verify(token, hashed_password)

@route.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.login_id == credentials.login_id)
    )

    db_user = result.scalars().first()
    if db_user is None or not verify_password(credentials.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = create_access_token(db_user.id)
    refresh_token = create_refresh_token(db_user.id)
    user_out = await _build_user_output(db_user, db)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_expires_in=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        user=user_out,
    )

@route.post("/auth/refresh", response_model=TokenResponse)
async def refresh_tokens(
    payload: TokenRefreshRequest, db: AsyncSession = Depends(get_db)
):
    token_config = decode_token(payload.refresh_token, expected_type="refresh")
    result = await db.execute(
        select(User).where(User.id == token_config.user_id)
    )
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token(user.id, token_config.scopes)
    refresh_token = create_refresh_token(user.id, token_config.scopes)
    user_out = await _build_user_output(user, db)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_expires_in=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        user=user_out,
    )

@route.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.login_id == user.login_id)
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="id already registered")

    new_user = User(
        name=user.name,
        login_id=user.login_id,
        password=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return await _build_user_output(new_user, db)

@route.get("/me", response_model=UserOut)
async def read_users_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, current_user.id)
    return await _build_user_output(user, db)

@route.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await _build_user_output(user, db)

@route.put("/{user_id}/changepassword", status_code=status.HTTP_200_OK)
async def change_password(
    password_change: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(password_change.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Old password does not match")
    current_user.password = hash_password(password_change.new_password)
    await db.commit()
    return {"detail": "Password changed successfully"}
