

from ai.models.ai_image_record import ImageCreateRecord
from wx.models.base_model import BaseModel

from django.db import models


class PromptExampleImageModel(BaseModel):
    class Meta:
        db_table = "z_prompt_example_image"
        verbose_name = "示例Prompt"
        verbose_name_plural = verbose_name

    create_image_record = models.ForeignKey(
        verbose_name="创建图片记录", to=ImageCreateRecord, on_delete=models.DO_NOTHING, null=True, blank=True)

    def ToJsonObj(self):
        r = self.create_image_record.ToJsonObj()
        r['created_at'] = self.created_at
        r['article_id'] = self.id
        return r
