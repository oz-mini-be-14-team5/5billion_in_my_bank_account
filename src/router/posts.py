from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import date
from tortoise.exceptions import DoesNotExist

from src.model.users import User
from src.model.posts import Post
from src.tools.jwt import get_current_user
from src.model.schema.post import PostCreate, PostUpdate, PostOut

router = APIRouter(
    prefix="/api/v1/posts",
    tags=["post"],          
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostOut)
async def create_post(
    post_data: PostCreate,
    user: User = Depends(get_current_user)
):
    try:
        post = await Post.create(
            author=user,
            title=post_data.title,
            content=post_data.content,
            date=post_data.date,
            image_url=None
        )
        return PostOut.from_orm(post)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일기 생성 중 오류 발생: {e}"
        )

@router.get("/", response_model=List[PostOut])
async def get_my_posts(
    page: int = Query(1, ge=1, description="페이지 번호"), 
    limit: int = Query(10, ge=1, le=100, description="페이지 당 항목 수"), 
    user: User = Depends(get_current_user) 
):
    posts_query = Post.filter(author=user)\
                      .offset((page - 1) * limit)\
                      .limit(limit)\
                      .order_by("date")
    return await PostOut.from_queryset(posts_query)

@router.get("/{post_id}", response_model=PostOut)
async def get_my_post(
    post_id: int,
    user: User = Depends(get_current_user)
):
    
    try:
        post = await Post.get(id=post_id, author_id=user.id) 
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="게시물을 찾을 수 없거나 조회 권한이 없습니다.")
    
    return PostOut.from_orm(post)


@router.put("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    user: User = Depends(get_current_user)
):

    try:
        post = await Post.get(id=post_id, author_id=user.id) 
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="수정할 게시물을 찾을 수 없거나 권한이 없습니다.")
    
    update_data = post_data.dict(exclude_unset=True) 
    await post.update_from_dict(update_data).save()
    return PostOut.from_orm(post)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    user: User = Depends(get_current_user)
):
    
    deleted_count = await Post.filter(id=post_id, author_id=user.id).delete()

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="삭제할 게시물을 찾을 수 없거나 권한이 없습니다.")
    
    return