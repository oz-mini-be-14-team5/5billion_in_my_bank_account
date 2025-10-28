from pydantic import BaseModel

class QuestionResponse(BaseModel):
    id: int
    message: str