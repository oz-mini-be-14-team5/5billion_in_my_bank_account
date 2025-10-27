from tortoise import fields, models

class Bookmark(models.Model):
	id = fields.IntField(pk=True)
	user = fields.ForeignKeyField("models.User", related_name="bookmarks") # on_delete는 기본값인 CASCADE를 사용하거나 명시적으로 설정할 수 있습니다.
	quote = fields.ForeignKeyField("models.Quote", related_name="bookmarks") # 'Quotes'를 'Quote'로 수정하고 related_name을 'bookmarks'로 통일
	created_at = fields.DatetimeField(auto_now_add=True)