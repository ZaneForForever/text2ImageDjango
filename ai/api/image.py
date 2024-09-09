

import datetime
import uuid
import io
import json
import os
from django.http import HttpRequest, JsonResponse
from PIL import Image

from django.views.decorators.csrf import csrf_exempt
from ai.api import image_service
from ai.models.article import ArticleModel
from ai.models.download_task import DownloadTask
from ai.models.platform_settings import PlatformSettingModel
from ai.models.post_params_config import ParamsFieldModel, ParamsFieldValueModel
from ai.multi_progress import create_images_progress
from ai.third import baidu_translate, stability_ai, thenextleg_io
from ai.models.ai_image_record import ImageCreateRecord
from ai.models.api_key import ApiKey, PlatformEngine
from ai.models import api_key

from util.django_request_decorator import check_user_ai_permission, convert_post_json_2_get_params, convert_session_to_wx_user
from util.loo import Loo
from util.number_util import NumberUtil


from wx.models.ai_permission import PermissionType
from wx.models.wx_user_model import WxUser


@csrf_exempt
@convert_post_json_2_get_params(required_fields=["session"])
@convert_session_to_wx_user
def UserCreateRecords(request: HttpRequest):
    user: WxUser = request.GET.get("wx_user")

    offset = request.GET.get("offset", 0)
    count = request.GET.get("count", 10)
    data = ImageCreateRecord.objects.filter(
        wx_user=user).order_by('-id')[offset:offset+count]
    data = [i.ToJsonObjSafe() for i in data]
    return JsonResponse({"code": 0, "data": data})


@csrf_exempt
@convert_post_json_2_get_params(required_fields=["session", "record_id"])
@convert_session_to_wx_user
def get_async_images(request: HttpRequest):
    user: WxUser = request.GET.get("wx_user")

    r: ImageCreateRecord = ImageCreateRecord.objects.filter(
        id=request.GET.get("record_id")).first()
    if r is None:
        return JsonResponse({"code": 1, "msg": "没有找到记录"})

    if r.wx_user_id != user.id:
        # 如果不是你的图片而且不是公开的，那就是非法请求
        if ArticleModel.objects.filter(image_create_record=r).exists() == False:
            return JsonResponse({"code": 1, "msg": "不是你的图片"})

    return JsonResponse({"code": 0, "data": r.ToJsonObj()})
    pass


@csrf_exempt
@convert_post_json_2_get_params(required_fields=["extra_image"])
@check_user_ai_permission(permission_name=PermissionType.AI_IMAGE)
def upscale_image(request: HttpRequest):
    r: ImageCreateRecord = ImageCreateRecord()


    r.extra_image = request.GET.get("extra_image")

    image_content = image_service.GetImageFromUrl(r.extra_image)

    if not image_content:
        return JsonResponse({"code": 1, "msg": "图片无效"})

    if len(image_content) > 5*1024*1024:
        return JsonResponse({"code": 1, "msg": "图片大小不能超过5M"})


    r.wx_user = request.GET.get("wx_user")

    r.create_type = ImageCreateRecord.IMAGE_UPSCALE
    r.api_platform_type = ApiKey.PLATFORM_STABILITY_AI

    r.uuid = NumberUtil.createUUID(suffix=r.wx_user.id)

    r.platform_engine = PlatformEngine.objects.filter(
        is_upscale=True).order_by("sort").first()

    r.request_host = request.META.get("HTTP_HOST")

    if r.platform_engine is None:
        return JsonResponse({"code": 1, "msg": "没有找到默认引擎"})

    r.save()

    create_images_progress.create_background(r)

    return JsonResponse({"code": 0, "data": r.ToJsonObj()})


@csrf_exempt
@convert_post_json_2_get_params(required_fields=["prompt_text", "params"])
@check_user_ai_permission(permission_name=PermissionType.AI_IMAGE)
def Text2ImageV2(request: HttpRequest):
    r: ImageCreateRecord = ImageCreateRecord()

    r.wx_user = request.GET.get("wx_user")

    r.uuid = NumberUtil.createUUID(suffix=r.wx_user.id)

    r.create_status = ImageCreateRecord.STATUS_INIT

    r.source_prompt_text = request.GET.get("prompt_text")

    r.source_negative_prompt = request.GET.get("negative_prompt_text", "")

    r.params = request.GET.get("params", None)

    default_params = ParamsFieldModel.default_params()
    if r.params is not None:
        for i in r.params:
            default_params[i] = r.params[i]

    r.params = default_params

    r.extra_image = request.GET.get("extra_image")

    r.create_type = ImageCreateRecord.TEXT_2_IMAGE if r.extra_image is None else ImageCreateRecord.IMAGE_2_IMAGE

    r.request_host = request.META.get("HTTP_HOST")
    auto_translate = r.get_params_value("auto_translate")
    if auto_translate == "0":
        r.prompt_text = r.source_prompt_text
        pass
    else:
        try:
            r.prompt_text = baidu_translate.Translate(r.source_prompt_text)
            # 翻译反词
            if r.source_negative_prompt and len(r.source_negative_prompt) > 0:
                Loo.info(r.source_negative_prompt)
                r.negative_prompt = baidu_translate.Translate(
                    r.source_negative_prompt)
        except Exception as e:
            Loo.err("百度翻译出错了")
            Loo.err(e)
            return JsonResponse({"code": -1, "msg": str(e)}, safe=False)
            pass

    r.is_async = True

    r.api_platform_type = ApiKey.PLATFORM_STABILITY_AI

    # if PlatformSettingModel.Get_Value_By_Code("force_use_stability_ai").value_bool == True or request.GET.get("sd") == True:

    #     pass
    r.create_status = ImageCreateRecord.STATUS_API_PROCESSING

    if r.isSdWebUIApi():

        r.api_platform_type = ApiKey.PLATFORM_SD_WEB_UI_API
        p: ParamsFieldValueModel = r.get_params_model("style")

        if p:
            r.prompt_text = f"{r.prompt_text},{p.api_value_extra}"
            r.negative_prompt = f"{r.negative_prompt},{ p.api_negative_extra}".replace(
                "None", "")
            pass

        pass
    elif r.isMidJourneyFromParams():
        r.api_platform_type = ApiKey.PLATFORM_ZHI_SHU
        # r.api_platform_type = ApiKey.PLATFORM_THENEXTLEG_IO
        # r.create_status = ImageCreateRecord.STATUS_ORDERING
        # if PlatformSettingModel.is_mid_journey_open() == True:

        # r.save()
        pass
    else:
        pass

    r.save()

    if r.api_platform_type != ApiKey.PLATFORM_SD_WEB_UI_API:

        create_images_progress.create_background(r)

    return JsonResponse({"code": 0, "data": r.ToJsonObj()})
