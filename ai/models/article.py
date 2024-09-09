
import json
from django.db import models

from ai.models.ai_image_record import ImageCreateRecord
from wx.models.base_model import BaseModel
from wx.models.wx_user_model import WxUser
from util import time_util


class ArticleModel(BaseModel):
    class Meta:
        db_table = "z_article"
        verbose_name = "广场文章"
        verbose_name_plural = verbose_name

    title = models.CharField(
        verbose_name="标题", max_length=255, null=False, blank=False)
    image_create_record = models.ForeignKey(
        to=ImageCreateRecord, on_delete=models.DO_NOTHING, verbose_name="图片创建记录", null=True, blank=True)

    wx_user = models.ForeignKey(
        to=WxUser, on_delete=models.DO_NOTHING, verbose_name="微信用户", null=True, blank=True)

    def ToJsonObj(self):
        result = {
            "article_id": self.id,
            "title": self.title,
            "created_at": time_util.display_time_difference(self.created_at),
            "user": self.wx_user.ToJsonObjSafe(),
        }
        r: ImageCreateRecord = self.image_create_record
        result['images'] = json.loads(
            r.images) if r.images and r.create_status == ImageCreateRecord.STATUS_SUCCESS else []
        result['record_id'] = r.id
        return result
