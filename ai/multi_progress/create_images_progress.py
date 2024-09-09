

import os
import threading

import django


from ai.models.ai_image_record import ImageCreateRecord
from ai.models.post_params_config import ParamsFieldValueModel
from util import image_util


def create_background(r: ImageCreateRecord):
    p = threading.Thread(target=do_multi_process_task, args=[r.id])
    # p = multiprocessing.Process(target=do_multi_process_task, args=[taskIdString])
    p.start()


def can_use_the_next_leg_api_token():
    import datetime
    from ai.models.api_key import ApiKey
    for one in ApiKey.objects.filter(platform=ApiKey.PLATFORM_THENEXTLEG_IO, available=True):

        if one.last_use_time is None or (datetime.datetime.now()-one.last_use_time).seconds >= 3:
            one.last_use_time = datetime.datetime.now()
            one.save()
            return one.key
        pass
    return None


def do_stability_ai(r: ImageCreateRecord):
    default_styles = ['analog-film', 'anime', 'cinematic', 'comic-book', 'digital-art', 'enhance', 'fantasy-art', 'isometric',
                      'line-art', 'low-poly', 'modeling-compound', 'neon-punk', 'origami', 'photographic', 'pixel-art', '3d-model', 'tile-texture']

    from ai.models.api_key import ApiKey
    from ai.third import stability_ai
    from util.loo import Loo
    import json
    from ai.api import params_service

    try:
        key = ApiKey.objects.filter(
            platform=1).first().key

        count_value = r.get_params_value("count")

        width, height = r.get_base_size_from_params()
        if r.create_type != ImageCreateRecord.IMAGE_UPSCALE:

            r.samples = int(count_value if count_value else 1)

            params_model: ParamsFieldValueModel = r.get_params_model("style")

            if params_model is not None:

                if params_model.parent is not None and params_model.parent.post_value in default_styles:
                    r.style_preset = params_model.parent.post_value
                elif params_model.post_value in default_styles:
                    r.style_preset = params_model.post_value
                else:
                    r.style_preset = None

                if params_model.api_value_extra is not None and params_model.api_value_extra != "":
                    r.prompt_text += f",{params_model.api_value_extra}"
                pass

            prompts = [
                {
                    "text": r.prompt_text
                }
            ]
        if r.create_type == ImageCreateRecord.IMAGE_UPSCALE:

            width, height = image_util.optimize_image_size(width, height)
            result = stability_ai.UpscaleImage(r,
                                               api_key=key, engine_id=r.platform_engine.platform_engine_id, width=width, height=height)

            pass
        elif r.extra_image is not None and r.extra_image != "":
            result = stability_ai.image_2_image_v2(r, user_id=r.wx_user.id, api_key=key, engine_id=r.platform_engine.platform_engine_id, style_preset=r.style_preset,
                                                   extra_image=r.extra_image, text_prompt=r.prompt_text, samples=r.samples, width=width, height=height)
            pass
        else:
            result = stability_ai.text_2_image_v2(r, user_id=r.wx_user.id,
                                                  api_key=key, engine_id=r.platform_engine.platform_engine_id, text_prompts=prompts,  samples=r.samples, style_preset=r.style_preset, width=width, height=height,)

        # r.result_width = width
        # r.result_height = height
        r.images = json.dumps(result)
        r.big_images = r.images
        r.api_platform_type = ApiKey.PLATFORM_STABILITY_AI
        r.create_status = ImageCreateRecord.STATUS_SUCCESS
        r.save()

    except Exception as e:

        Loo.error(e)
        r.create_status = ImageCreateRecord.STATUS_FAILED

        r.response_text = str(e)
        r.save()
        # raise e
    pass
    pass


def convert_params_2_mid_journey_prompt_text(r: ImageCreateRecord):

    if r.extra_image is not None and r.extra_image != "":
        if r.extra_image.startswith("http"):
            header_host = ""
        else:
            header_host = "http://go.ai.tianshuo.vip"
        r.prompt_text = f"{header_host}{r.extra_image} {r.prompt_text}"

    style_value_model = r.get_params_value("style")
    if style_value_model is not None:
        if style_value_model != "default":
            r.prompt_text += f" {style_value_model}"
        else:
            r.prompt_text += " --v 5.1"

    ar_value_model = r.get_params_value("ar")
    if ar_value_model is not None:
        r.prompt_text = f"{r.prompt_text} --ar {r.get_params_value('ar')}"
        pass

    print(f"r.prompt_text: {r.prompt_text}")

    return r.prompt_text


def do_zhi_shu_yun(r: ImageCreateRecord):

    from ai.third import zhi_shu_yun
    from ai.models.api_key import ApiKey

    r.api_platform_type = ApiKey.PLATFORM_ZHI_SHU

    r.prompt_text = convert_params_2_mid_journey_prompt_text(r)

    r.create_status = ImageCreateRecord.STATUS_API_PROCESSING
    zhi_shu_yun.text2image(r)
    r.save()

    pass


def do_thenextleg_io(r: ImageCreateRecord, api_token: str,):
    import json

    from ai.third import thenextleg_io
    from ai.api import params_service
    from ai.models.post_params_config import ParamsFieldValueModel
    from ai.models.api_key import ApiKey
    r.api_platform_type = ApiKey.PLATFORM_THENEXTLEG_IO
    convert_params_2_mid_journey_prompt_text(r)
    try:

        thenextleg_io.text2image(
            r, api_token, r.prompt_text)
        r.create_status = ImageCreateRecord.STATUS_API_SUCCESS
        r.save()
    except Exception as e:
        r.create_status = ImageCreateRecord.STATUS_API_ERROR
        r.response_text = str(e)
        r.save()
    pass


def do_next_leg_image_describe(r: ImageCreateRecord):

    from ai.models.api_key import ApiKey
    from ai.third import thenextleg_io
    from ai.api import params_service
    from ai.models.post_params_config import ParamsFieldValueModel

    r.api_platform_type = ApiKey.PLATFORM_THENEXTLEG_IO

    token = can_use_the_next_leg_api_token()
    if token is None:
        r.create_status = ImageCreateRecord.STATUS_BUSYING
        r.response_text = "没有可用的api_key"
        r.save()
        return

    if r.extra_image.startswith("http"):
        header_host = ""
    else:
        header_host = "http://go.ai.tianshuo.vip"
    source_image = f"{header_host}{r.extra_image}"

    thenextleg_io.image_blend(token, source_image)

    r.create_status = ImageCreateRecord.STATUS_API_SUCCESS
    r.save()

    pass


def do_sd_web_ui_api(r: ImageCreateRecord):
    # send to rabbitmq

    pass


def create_images(r: ImageCreateRecord):
    from ai.models.api_key import ApiKey
    from ai.models.api_key import PlatformEngine

    if r.create_type == ImageCreateRecord.IMAGE_UPSCALE:
        do_stability_ai(r)
        return

    if r.api_platform_type == ApiKey.PLATFORM_ZHI_SHU:
        do_zhi_shu_yun(r)
        return

    if r.api_platform_type == ApiKey.PLATFORM_SD_WEB_UI_API:
        do_sd_web_ui_api(r)
        return

    # 强制使用稳定性AI
    # if r.api_platform_type == ApiKey.PLATFORM_STABILITY_AI:
    r.api_platform_type = ApiKey.PLATFORM_STABILITY_AI
    r.platform_engine = PlatformEngine.objects.filter(
        available=True).first()
    do_stability_ai(r)
    return

    # # 判断当前mid的key是否可用
    # next_leg_api_token = can_use_the_next_leg_api_token()

    # if next_leg_api_token is not None:
    #     r.api_platform_type = ApiKey.PLATFORM_THENEXTLEG_IO
    #     do_thenextleg_io(r, next_leg_api_token)
    # else:

    #     r.api_platform_type = ApiKey.PLATFORM_STABILITY_AI
    #     r.platform_engine = PlatformEngine.objects.filter(
    #         available=True).first()
    #     do_stability_ai(r)

    # pass


def do_multi_process_task(record_id: int):
    # time.sleep(5)
    if 'DJANGO_SETTINGS_MODULE' not in os.environ.keys():
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
        django.setup()
        # 添加 INSTALLED_APPS
        from django.conf import settings
        settings.INSTALLED_APPS += ('ai',)

    from ai.models.ai_image_record import ImageCreateRecord

    r: ImageCreateRecord = ImageCreateRecord.objects.get(id=record_id)

    r.create_status = ImageCreateRecord.STATUS_PROCESSING

    from ai.multi_progress.create_images_progress import create_images

    create_images(r)

    r.save()
