from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

from src.model.users import User
from src.model.posts import Post
from src.tools.jwt import get_current_user
from model.schema.post import PostCreate, PostUpdate, PostOut

router = APIRouter(
    prefix="/api/v1/posts",
    tags=["post"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostOut)
async def create_post(post_data: PostCreate, user: User = Depends(get_current_user)):
    post = await Post.create(**post_data.model_dump(), author=user)
    return await PostOut.from_tortoise_orm(post)

@router.get("/", response_model=List[PostOut])
async def get_my_posts(page: int = 1, limit: int = 10, user: User = Depends(get_current_user)):
   
    posts = await Post.filter(author=user).offset((page - 1) * limit).limit(limit).order_by("-created_at")
    return [await PostOut.from_tortoise_orm(p) for p in posts]


@router.get("/{post_id}", response_model=PostOut)
async def get_my_post(post_id: int, user: User = Depends(get_current_user)):
    try:
        post = await Post.get(id=post_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다.")

    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="이 게시물을 조회할 권한이 없습니다.")
    
    return await PostOut.from_tortoise_orm(post)

@router.put("/{post_id}", response_model=PostOut)
async def update_post(post_id: int, post_data: PostUpdate, user: User = Depends(get_current_user)):
    try:
        post = await Post.get(id=post_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="수정할 게시물을 찾을 수 없습니다.")

    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="이 게시물을 수정할 권한이 없습니다.")

    update_data = post_data.model_dump(exclude_unset=True)
    await post.update_from_dict(update_data).save()
    return await PostOut.from_tortoise_orm(post)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, user: User = Depends(get_current_user)):
    try:
        post = await Post.get(id=post_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="삭제할 게시물을 찾을 수 없습니다.")

    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="이 게시물을 삭제할 권한이 없습니다.")

    await post.delete()
    return