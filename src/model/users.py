from hashlib import sha256

from passlib.context import CryptContext
from tortoise import fields
from tortoise.models import Model
import typing

from config import password_salt

if typing.TYPE_CHECKING:
    from src.model.posts import Post
    from src.model.bookmarks import Bookmark

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class User(Model):
    
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50) # 사용자 이름 (중복가능)
    created_at = fields.DatetimeField(auto_now_add=True)
    login_id = fields.CharField(max_length=50, unique=True)
    hash_password = fields.CharField(max_length=255)

    number_of_posts = fields.IntField(default=0)
    posts = fields.ReverseRelation["Post"]

    bookmarks: fields.ReverseRelation["Bookmark"]

    def __str__(self) -> str:
        return self.username

    def _get_percentage_of_posts(self) -> float:
        expected_posts = self.created_at.date().toordinal()
        if expected_posts == 0:
            return 0.0
        return (self.number_of_posts / expected_posts) * 100
    
    def _salt_password(self, password: str) -> str:
        salted = f"{password}{password_salt}".encode("utf-8")
        return sha256(salted).hexdigest()

    def set_password(self, password: str) -> None:
        self.hash_password = pwd_context.hash(self._salt_password(password))

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(self._salt_password(password), self.hash_password)