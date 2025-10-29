import json
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional, Tuple, Type, TypeVar

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import DoesNotExist

from src.model.posts import Post
from src.model.schema.post import PostUpdate
from src.model.users import User
from src.tools.image import _process_image
from src.tools.jwt import get_current_user

PostOut = pydantic_model_creator(
    Post,
    name="PostOut",
    include=("id", "title", "date", "content", "image_url", "created_at"),
)

router = APIRouter(
    prefix="/api/v1/posts",
    tags=["post"],
    responses={404: {"description": "Not found"}},
)


class ImageUploadResponse(BaseModel):
    image_url: str


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostOut)
async def create_post(
    title: str = Form(...),
    date: date = Form(...),
    content: str = Form(...),
    user: User = Depends(get_current_user),
):
    try:
        post = await Post.create(
            author=user,
            title=title,
            content=content,
            date=date,
        )
        return await PostOut.from_tortoise_orm(post)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {exc}",
        ) from exc


@router.post(
    "/{post_id}/image",
    status_code=status.HTTP_201_CREATED,
    response_model=ImageUploadResponse,
)
async def image_upload(
    post_id: int,
    user: User = Depends(get_current_user),
    image_file: UploadFile = File(...),
):
    try:
        target_post = await Post.get(id=post_id, author=user)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found or access denied.")

    image_path = await _process_image(image_file, user.id)
    target_post.image_url = image_path
    await target_post.save()
    return ImageUploadResponse(image_url=image_path)


@router.get("/", response_model=List[PostOut])
async def get_my_posts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    user: User = Depends(get_current_user),
):
    posts_query = (
        Post.filter(author=user)
        .offset((page - 1) * limit)
        .limit(limit)
        .order_by("date")
    )
    return await PostOut.from_queryset(posts_query)


@router.get("/by-week", response_model=List[PostOut])
async def get_posts_by_week(
    target_date: date = Query(..., description="Date to inspect"),
    user: User = Depends(get_current_user),
):
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    posts_query = (
        Post.filter(author=user)
        .filter(date__gte=start_of_week, date__lte=end_of_week)
        .order_by("date")
    )
    return await PostOut.from_queryset(posts_query)


@router.get("/image/{post_id}")
async def get_post_image(
    post_id: int,
    user: User = Depends(get_current_user),
):
    try:
        post = await Post.get(id=post_id, author=user)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found or access denied.")
    if not post.image_url:
        raise HTTPException(status_code=404, detail="Image not found")

    image_path = Path(post.image_url)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)


@router.get("/{post_id}", response_model=PostOut)
async def get_my_post(
    post_id: int,
    user: User = Depends(get_current_user),
):
    try:
        post = await Post.get(id=post_id, author_id=user.id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found or access denied.")

    return await PostOut.from_tortoise_orm(post)


ModelT = TypeVar("ModelT", bound=BaseModel)


def _parse_json_or_none(raw: Optional[object]) -> dict:
    if raw in (None, "", b""):
        return {}
    try:
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        if isinstance(raw, str):
            return json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return {}


async def _extract_upload(candidate) -> Optional[UploadFile]:
    if isinstance(candidate, UploadFile):
        if candidate.filename:
            return candidate
        await candidate.close()
    return None


async def _parse_payload(
    request: Request,
    model: Type[ModelT],
) -> Tuple[ModelT, Optional[UploadFile]]:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        raw_payload = form.get("post_data")
        if isinstance(raw_payload, UploadFile):
            try:
                raw_bytes = await raw_payload.read()
                raw_payload = raw_bytes.decode("utf-8")
            finally:
                await raw_payload.close()

        data_dict = _parse_json_or_none(raw_payload)
        if not data_dict:
            data_dict = {}
            for field_name in model.model_fields:
                value = form.get(field_name)
                if value not in (None, ""):
                    data_dict[field_name] = value

        instance = model(**data_dict)
        upload = await _extract_upload(form.get("image_file"))
        return instance, upload

    payload = await request.json()
    instance = model(**payload)
    return instance, None


@router.put("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    request: Request,
    user: User = Depends(get_current_user),
):
    try:
        post = await Post.get(id=post_id, author_id=user.id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found or access denied.")

    post_data, image_file = await _parse_payload(request, PostUpdate)
    update_data = post_data.dict(exclude_unset=True)

    if image_file is not None:
        new_image_path = await _process_image(image_file, user.id)
        if post.image_url:
            try:
                existing_path = Path(post.image_url)
                if existing_path.exists():
                    existing_path.unlink()
            except Exception:
                pass
        update_data["image_url"] = new_image_path

    await post.update_from_dict(update_data).save()
    return await PostOut.from_tortoise_orm(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
):
    deleted_count = await Post.filter(id=post_id, author_id=user.id).delete()

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found or access denied.")
    return
