from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import DoesNotExist

from src.model.quotes import Quote
from src.model.bookmarks import Bookmark
from src.tools.jwt import get_current_user
router = APIRouter(
    prefix="/api/v1/quotes",
    tags=["quote"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_random_quote():
    # 랜덤 명언 반환 api 구현
    return

@router.post("/bookmark/{quote_id}")
async def bookmark_quote(quote_id: int, user=Depends(get_current_user)):
    # 명언 북마크 추가 api 구현
    return