

import json
from django.db import models
from ai.models.ai_image_record import ImageCreateRecord
from ai.models.api_key import ApiKey, PlatformEngine

from wx.models.base_model import BaseModel
from wx.models.wx_user_model import WxUser


class WebhookRecord(BaseModel):

    class Meta:
        db_table = "z_record_webhook"
        verbose_name = "回调记录"
        verbose_name_plural = verbose_name
        pass

    request_text = models.TextField(verbose_name="请求内容", null=True, blank=True)
    request_path = models.CharField(
        max_length=255, verbose_name="请求路径", null=True, blank=True)

    request_ip = models.CharField(
        verbose_name="请求IP", max_length=255, null=True, blank=True)

    request_type = models.CharField(
        verbose_name="请求类型", max_length=255, null=True, blank=True)

    originatingMessageId = models.CharField(
        verbose_name="消息ID", max_length=255, null=True, blank=True)

    buttonMessageId = models.CharField(
        verbose_name="按钮消息ID", max_length=255, null=True, blank=True)
