

import json
from django.conf import settings


import requests

from ai.models.ai_image_record import ImageCreateRecord
from ai.models.api_key import ApiKey
from ai.models.platform_settings import PlatformSettingModel
from util.loo import Loo


def text2image(r: ImageCreateRecord):

    is_slow = PlatformSettingModel.is_zhi_shu_yun_slow()

    url = 'https://api.zhishuyun.com/midjourney/imagine'

    if is_slow:
        url += '/relax'

    query_platform = ApiKey.PLATFORM_ZHI_SHU_SLOW if is_slow else ApiKey.PLATFORM_ZHI_SHU
    api_key_object: ApiKey = ApiKey.objects.filter(platform=query_platform).filter(
        available=True).order_by("-id").first()

    r.api_key = api_key_object

    if api_key_object is None or api_key_object.key is None or api_key_object.key == "":
        r.response_text = "Missing ZhiShu API key."
        r.create_status = ImageCreateRecord.STATUS_NOT_API_TOKEN
        r.save()
        raise Exception("Missing ZhiShu API key.")

    api_key_object.use_once()

    token = api_key_object.key

    url += f"?token={token}"

    payload = json.dumps({
        "prompt": r.prompt_text,
        "action": "generate",
        "callback_url": "https://go.ai.tianshuo.vip/ai/webhook/zhishuyun.com/imageine",
        "image_origin": "https://cdn.discordapp.com"
    })

    r.request_text = payload

    headers = {
        # 'Authorization': f'Bearer {token}',
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    r.save()
    response = requests.request("POST", url, headers=headers, data=payload)

    r.response_text = f"{response.status_code} {response.text}"
    r.save()

    if response.status_code != 200:
        r.create_status = ImageCreateRecord.STATUS_API_ERROR
        r.response_text = f"{response.status_code} {response.text}"
        r.save()
        Loo.err(
            f"Non-200 response: {response.status_code} " + str(response.text))
        raise Exception("Non-200 response: " + str(response.text))

    resp_json = response.json()

    json_field_key = "task_id"

    if json_field_key not in resp_json or resp_json[json_field_key] == "":
        r.create_status = ImageCreateRecord.STATUS_API_ERROR
        Loo.err(
            f"Non-200 response: {response.status_code} " + str(response.text))
        r.save()
        raise Exception("Non-200 response: " + str(response.text))

    r.message_id = resp_json[json_field_key]
    r.create_status = ImageCreateRecord.STATUS_API_SUCCESS

    r.save()
    pass
