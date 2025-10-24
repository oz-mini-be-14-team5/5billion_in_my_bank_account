from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import DoesNotExist

from src.model.users import User
from src.model.posts import Post
from src.tools.jwt import get_current_user

router = APIRouter(
    prefix="/api/v1/posts",
    tags=["post"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def create_post(user: User = Depends(get_current_user)):
    # 게시물 생성 api 구현
    return

@router.get("/{user_id}")
async def get_post(user_id:int , page: int, user: User = Depends(get_current_user)):
    # 게시물 목록 조회 api 구현
    return

@router.get("/{user_id}/{post_id}")
async def get_post(user_id:int , post_id: int, user: User = Depends(get_current_user)):
    # 특정 게시물 조회 api 구현
    return

@router.put("/{post_id}")
async def update_post(post_id: int, user: User = Depends(get_current_user)):
    # 게시물 수정 api 구현
    return

@router.delete("/{post_id}")
async def delete_post(post_id: int, user: User = Depends(get_current_user)):
    # 게시물 삭제 api 구현
    return