
from django.contrib import admin, messages

from ai.models.ai_image_record import ImageCreateRecord
from wx.models.base_model import BaseModel
from django.db import models


class CrontabRecord(BaseModel):
    class Meta:
        db_table = "z_record_crontab"
        verbose_name = "定时任务记录"
        verbose_name_plural = verbose_name

    end_time = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)

    crontab_minute = models.CharField(
        verbose_name="分钟", max_length=255, null=False, blank=False)

    crontab_times = models.IntegerField(
        verbose_name="次数", null=False, blank=False, default=0)

    # images = models.ManyToManyField(
    #     to=ImageCreateRecord, through="CrontabCreateImage", verbose_name="图片创建记录", null=True, blank=True)

    pass


class CrontabCreateImage(BaseModel):
    class Meta:
        db_table = "z_record_crontab_create_image"
        verbose_name = "定时任务创建图片记录"
        verbose_name_plural = verbose_name
        pass

    crontab_record = models.ForeignKey(
        to=CrontabRecord, related_name="crontab_records", on_delete=models.DO_NOTHING, verbose_name="定时任务记录", null=True, blank=True)
    create_image = models.ForeignKey(
        to=ImageCreateRecord, related_name="image_records", on_delete=models.DO_NOTHING, verbose_name="图片创建记录", null=True, blank=True)
