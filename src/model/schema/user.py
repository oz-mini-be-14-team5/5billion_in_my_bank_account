from pydantic import BaseModel
from pydantic import Field

class UserCreate(BaseModel):
    username: str
    login_id: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    number_of_posts: int

class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str

class UserUpdateUsername(BaseModel):
    new_username: str

class UserDelete(BaseModel):
    password: str