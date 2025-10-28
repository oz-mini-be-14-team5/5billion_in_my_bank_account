from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import DoesNotExist
from typing import List
import random

from src.model.quotes import Quote
from src.model.bookmarks import Bookmark
from src.model.schema.quote import QuoteResponse
from src.tools.jwt import get_current_user

router = APIRouter(
    prefix="/api/v1/quotes",
    tags=["quote"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=QuoteResponse)
async def get_random_quote():
    # 랜덤 명언 반환 api 구현
    total = await Quote.all().count()
    if total == 0:
        return None

    idx = random.randrange(total)

    result = await Quote.all().offset(idx).limit(1)
    return result[0]

@router.post("/bookmark/{quote_id}", status_code=201)
async def bookmark_quote(quote_id: int, user=Depends(get_current_user)):
    # 명언 북마크 추가 api 구현
    try:
        quote = await Quote.get(id=quote_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Quote not found")

    bookmark, created = await Bookmark.get_or_create(user=user, quote=quote)

    if not created:
        raise HTTPException(status_code=400, detail="Quote already bookmarked")

    return {"status": "success", "message": "Quote bookmarked successfully"}

@router.get("/bookmarks/", response_model=List[QuoteResponse]) 
async def get_bookmarked_quotes(user=Depends(get_current_user)):
    # 북마크 리스트 조회
    await user.fetch_related("bookmarks", "bookmarks__quote")
    bookmarked_quotes = [bookmark.quote for bookmark in user.bookmarks]
    return bookmarked_quotes

@router.delete("/bookmark/{quote_id}", status_code=204) 
async def delete_bookmark(quote_id: int, user=Depends(get_current_user)):
    # 북마크 삭제
    try:
        quote = await Quote.get(id=quote_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Quote not found")

    deleted_count = await Bookmark.filter(user=user, quote=quote).delete()

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    return