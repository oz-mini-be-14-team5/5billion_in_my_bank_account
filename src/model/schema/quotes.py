from pydantic import BaseModel

class QuoteResponse(BaseModel):
    id: int
    author: str
    message: str
