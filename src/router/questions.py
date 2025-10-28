from fastapi import APIRouter
import random

from src.model.questions import Question
from src.model.schema.question import QuestionResponse

router = APIRouter(
    prefix="/api/v1/questions",
    tags=["question"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=QuestionResponse)
async def get_random_question():
    total = await Question.all().count()
    if total == 0:
        return None

    idx = random.randrange(total)

    result = await Question.all().offset(idx).limit(1)
    return result[0]