

from django.db import models

# Create your models here.

from wx.models.base_model import BaseModel


class ApiKey(BaseModel):

    PLATFORM_UNABLE = 0
    PLATFORM_STABILITY_AI = 1
    PLATFORM_THENEXTLEG_IO = 2
    PLATFORM_ZHI_SHU = 3
    PLATFORM_ZHI_SHU_SLOW = 4
    PLATFORM_SD_WEB_UI_API = 5

    platform_choices = (
        (PLATFORM_UNABLE, "失效"),
        (PLATFORM_STABILITY_AI, "Stabilibity AI"),
        (PLATFORM_THENEXTLEG_IO, "THENEXTLEG_IO"),
        (PLATFORM_ZHI_SHU, "知数云api"),
        (PLATFORM_ZHI_SHU_SLOW, "知数云api(慢速)"),
        (PLATFORM_SD_WEB_UI_API, "SD_WEB_UI_API"),
    )

    CREATE_TYPE_SYNC = 0
    CREATE_TYPE_ASYNC = 1

    create_type_choices = (
        (CREATE_TYPE_SYNC, "同步"),
        (CREATE_TYPE_ASYNC, "异步"),
    )

    class Meta:
        db_table = "z_api_key"
        verbose_name = "API Key"
        verbose_name_plural = verbose_name

    name = models.CharField(max_length=100, verbose_name="名称")
    key = models.CharField(max_length=100, unique=True)

    remark = models.TextField(
        max_length=100, verbose_name="备注", null=True, blank=True)

    platform = models.IntegerField(verbose_name="平台", null=False, blank=False,
                                   choices=platform_choices, default=0)

    available = models.BooleanField(verbose_name="可用", default=False)

    request_type = models.IntegerField(
        verbose_name="创建类型", choices=create_type_choices, null=False, blank=False, default=0)

    last_use_time = models.DateTimeField(
        verbose_name="最后使用时间", null=True, blank=True)

    use_times = models.IntegerField(
        verbose_name="使用次数", null=False, blank=False, default=0)

    def __str__(self) -> str:
        return f"{self.get_platform_display()}:{self.id}"

    def use_once(self):
        self.use_times += 1
        self.save()
        pass


class PlatformEngine(BaseModel):

    class Meta:
        db_table = "z_platform_engine"
        verbose_name = "平台引擎"
        verbose_name_plural = verbose_name

    available = models.BooleanField(verbose_name="可用", default=False)

    name = models.CharField(max_length=100, verbose_name="名称")

    platform_engine_id = models.CharField(
        max_length=100, verbose_name="平台引擎id", null=True, blank=True)

    remark = models.TextField(
        max_length=1024, verbose_name="备注", null=True, blank=True)

    platform = models.IntegerField(verbose_name="平台", null=False, blank=False,
                                   choices=ApiKey.platform_choices, default=0)

    type_name = models.CharField(
        max_length=100, verbose_name="类型名称", null=True, blank=True)

    is_upscale = models.BooleanField(verbose_name="是否是Upscale", default=False)

    sort = models.IntegerField(
        verbose_name="排序", null=False, blank=False, default=0)

    def ToJsonObj(self):
        return {
            "name": self.name,
            "platform_engine_id": self.platform_engine_id,
            "remark": self.remark,
            "type_name": self.type_name,
        }

    def __str__(self) -> str:
        return f" {self.platform_engine_id}"
