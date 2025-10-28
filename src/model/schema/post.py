from pydantic import BaseModel, ConfigDict
import datetime
from src.model.posts import Post

# PostCreate, PostUpdate, PostOut

class PostCreate(BaseModel):
    title : str
    date : datetime.date
    content : str
    model_config = ConfigDict(from_attributes=True)

class PostUpdate(BaseModel):
    title : str
    content : str
    model_config = ConfigDict(from_attributes=True)

class PostOut(BaseModel):
    title : str
    date : datetime.date
    content : str
    created_at : datetime.datetime
    model_config = ConfigDict(from_attributes=True)