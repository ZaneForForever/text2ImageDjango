

import hashlib
from django.conf import settings
import requests

BAIDU_TRANSLATE_API_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"


def Translate(text: str):

    salt = "1435660288"
    sign: str = settings.BAIDU_TRANSLATE_APPID + \
        text + "1435660288" + settings.BAIDU_APP_SECRET

    sign_md5 = hashlib.md5(sign.encode("utf-8")).hexdigest()
    response = requests.post(
        BAIDU_TRANSLATE_API_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },

        data={
            "q": text,
            "from": "auto",
            "to": "en",
            "appid": settings.BAIDU_TRANSLATE_APPID,
            "salt": salt,
            "sign": sign_md5
        },

    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    return ','.join([i["dst"] for i in response.json()["trans_result"]])
