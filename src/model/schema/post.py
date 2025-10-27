from pydantic import BaseModel
import datetime
from src.model.posts import Post

# PostCreate, PostUpdate, PostOut

class PostCreate(BaseModel):
    title : str
    date : datetime.date
    contents : str

class PostUpdate(BaseModel):
    title : str
    contents : str

class PostOut(BaseModel):
    title : str
    date : datetime.date
    contents : str
    created_at : datetime.datetime
    