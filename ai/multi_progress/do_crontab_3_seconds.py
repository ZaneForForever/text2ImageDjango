

import datetime
import json
from ai.api import image_service
from ai.models.ai_image_record import ImageCreateRecord
from ai.models.api_key import ApiKey
from ai.models.crontab_record import CrontabRecord
from ai.third import thenextleg_io
from util.loo import Loo


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


def run():
    current_minute_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cr: CrontabRecord = CrontabRecord.objects.get_or_create(crontab_minute=current_minute_str)[
        0]
    cr.crontab_times += 1

    r: ImageCreateRecord = image_service.GetOrderingImageTask()

    cr.image_record = r
    cr.save()

    # r = ImageCreateRecord.ob jects.get(id=223)

    if r is None:
        Loo.info("没有任务")
        return

    api_token = can_use_the_next_leg_api_token()
    if api_token is None:
        r.create_status = ImageCreateRecord.STATUS_BUSYING
        r.save()
        return

    Loo.info(f"开始处理任务{r.id}")

    r.api_platform_type = ApiKey.PLATFORM_THENEXTLEG_IO
    r.create_status = ImageCreateRecord.STATUS_API_PROCESSING
    r.save()

    if r.extra_image is not None and r.extra_image != "":
        if r.extra_image.startswith("http"):
            header_host = ""
        else:
            header_host = "http://go.ai.tianshuo.vip"
        r.prompt_text = f"{header_host}{r.extra_image} {r.prompt_text}"

    ar_value_model = r.get_params_value("ar")
    if ar_value_model is not None:
        # r.prompt_text = f"{r.prompt_text} --ar {r.get_params_value('ar')}"
        pass

    style_value_model = r.get_params_value("style")
    if style_value_model is not None:
        r.prompt_text += f",{style_value_model}"

    # try:

    r.response_text = thenextleg_io.text2image(
        r, api_token, r.prompt_text)
    r.create_status = ImageCreateRecord.STATUS_API_SUCCESS
    r.save()
    # except Exception as e:
    #     r.create_status = ImageCreateRecord.STATUS_API_ERROR
    #     r.response_text = str(e)
    #     r.save()
    pass

    cr.updated_at = datetime.datetime.now()
    cr.save()

    pass


def do_3_seconds_job():
    run()

    pass
