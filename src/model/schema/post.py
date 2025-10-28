from pydantic import BaseModel, ConfigDict
import datetime
from tortoise.contrib.pydantic import pydantic_model_creator

from src.model.posts import Post

# PostCreate, PostUpdate, PostOut

class PostUpdate(BaseModel):
    title: str
    content: str
    model_config = ConfigDict(from_attributes=True)