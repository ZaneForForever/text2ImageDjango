

from wx.models.base_model import BaseModel
from django.db import models

from wx.models.wx_user_model import WxUser


class RecordUploadImage(BaseModel):
    class Meta:
        db_table = "z_record_upload_image"
        verbose_name = "上传图片记录"
        verbose_name_plural = verbose_name
        pass

    

    scale_image = models.ImageField(
        verbose_name="缩放图片保存路径", upload_to="upload/scale", null=False, blank=False)
    
    source_image = models.ImageField(
        verbose_name="源图片保存路径", upload_to="upload/source", null=False, blank=False)

    wx_user = models.ForeignKey(
        to=WxUser, on_delete=models.DO_NOTHING, verbose_name="微信用户", null=False, blank=False)

    source_width = models.IntegerField(
        verbose_name="源图片宽度", null=True, blank=True)
    source_height = models.IntegerField(
        verbose_name="源图片高度", null=True, blank=True)
    scale_width = models.IntegerField(
        verbose_name="缩放图片宽度", null=True, blank=True)
    scale_height = models.IntegerField(
        verbose_name="缩放图片高度", null=True, blank=True)
