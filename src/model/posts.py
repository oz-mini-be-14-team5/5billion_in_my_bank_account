from tortoise import fields
from tortoise.models import Model

from src.model.users import User

# 일기 게시글 모델
class Post(Model):
    id = fields.IntField(pk=True)

    # 메타데이터
    title = fields.CharField(max_length=100)
    date = fields.DateField()

    content = fields.TextField()
    image_url = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    author: User = fields.ForeignKeyField("models.User", related_name="posts")

    def __str__(self):
        return self.title