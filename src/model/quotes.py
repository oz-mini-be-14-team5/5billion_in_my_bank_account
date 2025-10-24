from tortoise import fields
from tortoise.models import Model
import typing

if typing.TYPE_CHECKING:
    from src.model.users import User

class Quote(Model):
    id = fields.IntField(pk=True)
    author = fields.CharField(max_length=100)
    message = fields.TextField()
    bookmarked_by: fields.ReverseRelation["User"]