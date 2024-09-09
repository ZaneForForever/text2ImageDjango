

import json
from django.conf import settings


import requests

from ai.models.ai_image_record import ImageCreateRecord
from util.loo import Loo


TheNextleg_IO_API_URL = "https://api.thenextleg.io/v2"


def image_describe(r: ImageCreateRecord, token: str, image_url: str):

    url_path = "/imagine"

    url = f"{TheNextleg_IO_API_URL}{url_path}"

    payload = json.dumps({
        "url": image_url,
        "ref": r.uuid,
        "webhookOverride": "https://go.ai.tianshuo.vip/ai/webhook/thenextleg.io/describe"
    })

    r.request_text = payload

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    resp_json = json.loads(r.response_text)

    if "success" not in resp_json or resp_json["success"] is False or "messageId" not in resp_json or resp_json["messageId"] == "":
        raise Exception("Non-200 response: " + str(response.text))

    r.message_id = resp_json["messageId"]
    pass


def text2image(r: ImageCreateRecord, token: str, prompt_text: str):

    url_path = "/imagine"

    url = f"{TheNextleg_IO_API_URL}{url_path}"

    payload = json.dumps({
        "msg": prompt_text,
        # "ref": "",
        # "webhookOverride": ""
    })

    r.request_text = payload

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    r.response_text = f"{response.status_code} {response.text}"

    if response.status_code != 200:
        Loo.err(
            f"Non-200 response: {response.status_code} " + str(response.text))
        raise Exception("Non-200 response: " + str(response.text))

    resp_json = response.json()

    if "success" not in resp_json or resp_json["success"] is False or "messageId" not in resp_json or resp_json["messageId"] == "":
        Loo.err(
            f"Non-200 response: {response.status_code} " + str(response.text))
        raise Exception("Non-200 response: " + str(response.text))

    r.message_id = resp_json["messageId"]

    pass


def get_message_status(message_id: str):
    token = settings.THENEXTLEG_IO_API_TOKEN
    url_path = "/message"

    url = f"{TheNextleg_IO_API_URL}{url_path}/{message_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        pass

    return response.text
