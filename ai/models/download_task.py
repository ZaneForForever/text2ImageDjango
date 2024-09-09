

import json
from django.db import models
from ai.models.ai_image_record import ImageCreateRecord
from ai.models.api_key import ApiKey, PlatformEngine

from wx.models.base_model import BaseModel
from wx.models.wx_user_model import WxUser


class DownloadTask(BaseModel):

    
    
    class Meta:
        db_table = "z_record_download_task"
        verbose_name = "下载任务"
        verbose_name_plural = verbose_name
        pass

    STATUS_INIT = 0
    STATUS_DOWNLOADING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILED = 3

    download_status_choices = (
        (STATUS_INIT, "初始化"),
        (STATUS_DOWNLOADING, "下载中"),
        (STATUS_SUCCESS, "成功"),
        (STATUS_FAILED, "失败"),
    )

    image_create_record = models.ForeignKey(
        to=ImageCreateRecord, related_name="download_task", on_delete=models.DO_NOTHING, verbose_name="图片创建记录", null=True, blank=True)

    download_status = models.IntegerField(choices=download_status_choices,
                                          verbose_name="状态", null=False, blank=False, default=-1)

    from_url = models.TextField(
        verbose_name="下载地址", null=True, blank=True)
    save_path = models.CharField(
        max_length=255, verbose_name="保存路径", null=True, blank=True)

    start_time = models.DateTimeField(
        verbose_name="开始时间", null=True, blank=True)
    finish_time = models.DateTimeField(
        verbose_name="结束时间", null=True, blank=True)
    progress = models.IntegerField(verbose_name="进度", null=True, blank=True)

    def ToJsonObj(self):
        a = dict()
        a['id'] = self.id
        a["download_status"] = self.download_status
        a["from_url"] = self.from_url
        a["save_path"] = self.save_path
        return a
    
    def get_redis_key(self):
        return f"download_task_{self.id}"
