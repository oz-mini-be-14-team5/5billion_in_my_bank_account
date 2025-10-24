from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import DoesNotExist

from src.model.users import User
from src.model.questions import Question

router = APIRouter(
    prefix="/api/v1/questions",
    tags=["question"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_random_question():
    question_count = await Question.all().count()
    # 랜덤 질문 반환 api 구현
    return