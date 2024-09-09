

import io
import json
from django.db import models
import requests
import urllib3
from ai.models.api_key import ApiKey, PlatformEngine
from ai.models.post_params_config import ParamsFieldModel, ParamsFieldValueModel
from util.number_util import NumberUtil

from wx.models.base_model import BaseModel
from wx.models.wx_user_model import WxUser

from util import time_util
from util import image_util

from django.template.loader import render_to_string


class ImageCreateRecord(BaseModel):

    TEXT_2_IMAGE = 0
    IMAGE_2_IMAGE = 1
    IMAGE_UPSCALE = 2
    IMAGE_MASKING = 3
    IMAGE_BLEND = 4
    IMAGE_DESCRIBE = 5

    STATUS_INIT = 0
    STATUS_PROCESSING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILED = 3
    STATUS_API_SUCCESS = 4
    STATUS_API_ERROR = 5
    STATUS_WEBHOOK_SUCCESS = 6
    STATUS_WEBHOOK_ERROR = 7
    STATUS_BUSYING = 8
    STATUS_ORDERING = 9
    STATUS_API_PROCESSING = 10
    STATUS_WEBHOOK_PROCESSING = 11
    STATUS_DOWNLOAD_START = 12
    STATUS_NOT_API_TOKEN = 13
    STATUS_TASK_SEND = 14
    STATUS_TASK_START = 15
    STATUS_NOT_SD_MODEL = 16

    create_status_choice = (
        (STATUS_INIT, "初始化"),
        (STATUS_PROCESSING, "创建中"),
        (STATUS_FAILED, "失败"),
        (STATUS_SUCCESS, "成功"),
        (STATUS_API_SUCCESS, "API请求成功"),
        (STATUS_API_ERROR, "API失败"),
        (STATUS_WEBHOOK_SUCCESS, "Webhook成功"),
        (STATUS_WEBHOOK_ERROR, "Webhook失败"),
        (STATUS_BUSYING, "繁忙"),
        (STATUS_ORDERING, "排队中"),
        (STATUS_API_PROCESSING, "API处理中"),
        (STATUS_WEBHOOK_PROCESSING, "Webhook处理中"),
        (STATUS_DOWNLOAD_START, "下载中"),
        (STATUS_NOT_API_TOKEN, "没有可用的api_key"),
        (STATUS_TASK_SEND, "任务已经下发"),
        (STATUS_TASK_START, "任务已经开始"),
        (STATUS_NOT_SD_MODEL, "模型不存在"),

    )
    create_type_choices = (
        (TEXT_2_IMAGE, "文生图"),
        (IMAGE_2_IMAGE, "图生图"),
        (IMAGE_UPSCALE, "Upscale"),
        (IMAGE_MASKING, "Masking"),
        (IMAGE_BLEND, "图生文"),
    )

    class Meta:
        db_table = "z_record_image_create"
        verbose_name = "图片创建记录"
        verbose_name_plural = verbose_name
    pass

    uuid = models.CharField(verbose_name="任务ID",
                            max_length=100, null=True, blank=True)

    create_status = models.IntegerField(
        verbose_name="创建状态", choices=create_status_choice, null=False, blank=False, default=STATUS_INIT)

    create_type = models.IntegerField(
        verbose_name="创建类型", choices=create_type_choices, null=False, blank=False, default=0)

    source_image_save_path = models.CharField(
        verbose_name="源图片保存路径", max_length=2048, null=True, blank=True)

    wx_user = models.ForeignKey(
        to=WxUser, on_delete=models.DO_NOTHING, verbose_name="微信用户")

    platform_engine = models.ForeignKey(
        to=PlatformEngine, on_delete=models.DO_NOTHING, verbose_name="平台引擎", null=True, blank=True)

    api_key = models.ForeignKey(
        to=ApiKey, on_delete=models.DO_NOTHING, verbose_name="API Key", null=True, blank=True)

    api_platform_type = models.IntegerField(
        verbose_name="API平台类型", choices=ApiKey.platform_choices, null=True, blank=True)

    images = models.TextField(
        max_length=4096, verbose_name="图片列表", null=True, blank=True)

    big_images = models.TextField(
        max_length=4096, verbose_name="大图片列表", null=True, blank=True)

    result_width = models.IntegerField(
        verbose_name="结果图片宽度", null=True, blank=True)
    result_height = models.IntegerField(
        verbose_name="结果图片高度", null=True, blank=True)

    samples = models.IntegerField(
        verbose_name="样本数", null=True, blank=True, default=0)

    prompt_text = models.TextField(
        verbose_name="提示文本", null=True, blank=True)

    negative_prompt = models.TextField(
        verbose_name="反词", null=True, blank=True)

    source_negative_prompt = models.TextField(
        verbose_name="原始反词", null=True, blank=True)

    source_prompt_text = models.TextField(
        max_length=1000, verbose_name="原始提示文本", null=True, blank=True)

    response_text = models.TextField(
        verbose_name="响应文本", null=True, blank=True)

    request_text = models.TextField(verbose_name="请求文本", null=True, blank=True)

    message_id = models.CharField(
        verbose_name="消息id", max_length=100, null=True, blank=True)

    is_async = models.BooleanField(verbose_name="是否异步", default=False)

    params = models.JSONField(verbose_name="参数", null=True, blank=True)

    extra_image = models.CharField(
        verbose_name="额外图片", max_length=1000, null=True, blank=True)

    request_host = models.CharField(
        verbose_name="请求主机", max_length=1000, null=True, blank=True)

    def is_local(self):
        return "127.0.0.1:8000" in self.request_host and self.api_platform_type == ApiKey.PLATFORM_STABILITY_AI

    def ToJsonObj(self):
        if self.images:
            self.images = self.images.replace("http://", "https://")
        if self.big_images:
            self.big_images = self.big_images.replace("http://", "https://")

        result = {
            "record_id": self.id,
            "images": json.loads(self.images) if self.images and self.create_status == ImageCreateRecord.STATUS_SUCCESS else [],
            "big_images": json.loads(self.big_images) if self.big_images and self.create_status == ImageCreateRecord.STATUS_SUCCESS else [],
            "samples": self.samples,
            "prompt_text": self.source_prompt_text,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "create_type": self.create_type,
            "create_status": self.create_status,
            "create_status_display": self.get_create_status_display(),
            "extra_image": self.extra_image if self.extra_image else None,
            "api": self.api_key.__str__() if self.api_key else None,
            "is_async": self.is_async,
            "params": self.params if self.params else {},
            "params_display": self.params_display(),
            "result_width": self.result_width,
            "result_height": self.result_height,
            "can_upscale": self.create_type != ImageCreateRecord.IMAGE_UPSCALE,
            # "can_upscale": False,

        }

        if self.create_status in [ImageCreateRecord.STATUS_API_ERROR, ImageCreateRecord.STATUS_WEBHOOK_ERROR, ImageCreateRecord.STATUS_FAILED]:
            result["create_status"] = ImageCreateRecord.STATUS_FAILED

        return result

    def ToJsonObjSafe(self):

        if self.images:
            self.images.replace("http://", "https://")
        if self.big_images:
            self.big_images.replace("http://", "https://")

        title = self.source_prompt_text
        if self.create_type == ImageCreateRecord.IMAGE_UPSCALE:
            title = "高清精绘"
        result = {
            "record_id": self.id,
            "images": json.loads(self.images) if self.images and self.create_status == ImageCreateRecord.STATUS_SUCCESS else [],
            "title": title,
            "result_width": self.result_width,
            "result_height": self.result_height,
            "created_at": time_util.display_time_difference(self.created_at),
        }

        return result

    def __str__(self):
        return f"{self.id}-{self.prompt_text}-{self.get_create_status_display()}"

    def get_params_model(self, key) -> ParamsFieldValueModel:
        value: ParamsFieldValueModel = None
        if self.params and key in self.params:
            find_post_value = self.params[key]
            value = ParamsFieldValueModel.objects.filter(
                param_field__params_code=key, post_value=find_post_value).first()

        # params里面没有这个code，就去数据库里面找
        if value is None:
            field = ParamsFieldModel.objects.filter(
                params_code=key).first()
            # 非高级属性才赋值默认值
            if field is not None and field.is_advanced is False:
                value = field.default_value
        return value

    def get_params_value(self, key):
        value: ParamsFieldValueModel = None
        if self.params and key in self.params:
            find_post_value = self.params[key]
            value = ParamsFieldValueModel.objects.filter(
                param_field__params_code=key, post_value=find_post_value).first()

        # params里面没有这个code，就去数据库里面找
        if value is None:
            field = ParamsFieldModel.objects.filter(
                params_code=key).first()
            # 非高级属性才赋值默认值
            if field is not None and field.is_advanced is False:
                value = field.default_value
        if value is not None:
            if value.api_value_extra is not None and value.api_value_extra != "":
                return value.api_value_extra
            else:
                return value.post_value

        return None

    def isMidJourneyFromParams(self):
        value = self.get_params_value("use_mid_journey")

        return (value == "1")

    def isSdWebUIApi(self):
        value = self.get_params_value("use_mid_journey")

        return (value == "2")

    def get_base_size_from_params(self):

        if self.create_type == ImageCreateRecord.IMAGE_UPSCALE:
            if "http" in f"{self.extra_image}":
                image_file_fb = io.BytesIO(requests.get(self.extra_image).content)
            else:
                image_file_fb = open(self.extra_image[1:], "rb")
            return image_util.GetImageSize(image_file_fb)

        ar = self.get_params_value("ar").split(":")
        ar_width = int(ar[0])
        ar_height = int(ar[1])
        if ar_width > ar_height:
            width = 512
            height = int(512*ar_height/ar_width)
        else:
            height = 512
            width = int(512*ar_width/ar_height)
        # print(width, height)
        width = NumberUtil.find_nearest_multiple(width, 64)
        height = NumberUtil.find_nearest_multiple(height, 64)
        # print(width, height)
        return (width, height)

    def params_display(self):
        result = []

        self.params = self.params if self.params else {}

        for k, v in self.params.items():
            value = ParamsFieldValueModel.objects.filter(
                param_field__params_code=k, post_value=v).first()
            if value is not None:
                result.append(
                    {
                        "params_code": k,
                        "params_display": value.param_field.params_display,
                        "post_value": value.post_value,
                        "value_display": value.value_display,

                    })
            # field = ParamsFieldModel.objects.filter(
            #     params_code=k).first()
            # if field is not None:
                # result[field.params_display] = v

        extra_image_display = "是" if self.extra_image is not None and self.extra_image != "" else "无"

        result.append(
            {
                "params_display": "参考图片",
                "post_value": extra_image_display,
                "value_display": extra_image_display,

            })

        result.append(
            {
                "params_display": "prompt(raw)",
                "post_value": self.prompt_text,
                "value_display": self.prompt_text,

            })

        result.append(
            {
                "params_display": "任务ID",
                "post_value": self.uuid,
                "value_display": self.uuid,

            })

        return result
