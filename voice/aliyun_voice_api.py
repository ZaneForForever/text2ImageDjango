

import io
import os
import time
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from django.core.files.storage import default_storage

import requests

from ai.cache.cache_helper import CacheHelper
from util.loo import Loo


def get_token(id, secret):

    token = None
    # 创建AcsClient实例
    client = AcsClient(
        id, secret,
        "cn-shanghai"
    )

    # 创建request，并设置参数。
    request = CommonRequest()
    request.set_method('POST')
    request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
    request.set_version('2019-02-28')
    request.set_action_name('CreateToken')

    try:
        response = client.do_action_with_exception(request)
        print(response)

        jss = json.loads(response)
        if 'Token' in jss and 'Id' in jss['Token']:
            token = jss['Token']['Id']

            expireTime = jss['Token']['ExpireTime']
            # print("token = " + token)
            # print("expireTime = " + str(expireTime))
    except Exception as e:
        print(e)

    return token


def request_sound_api(sound_app_key, token, text, voice=None, format="wav", volume=80, speech_rate=0):
    """
    Args:
        sound_app_key (_type_): 应用的appkey

        token (_type_): 调用CreateToken接口获取的token
        text (_type_): 合成的文本
        voice (_type_): 语音合成的发音人，可选，默认是xiaoyun
        format (str, optional): 合成的音频格式，支持pcm,wav,mp3格式，默认是pcm
        volume (int, optional):  音量，范围是0~100，可选，默认80
        speech_rate (int, optional):语速，范围是-500~500，可选，默认是0
    Returns:
        _type_: _description_
    """

    url = "https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/tts"
    json_data = {
        "appkey": sound_app_key,
        "text": text,
        "token": token,
        "format": format,
        "volume": volume,
        "speech_rate": speech_rate,
    }

    if voice:
        json_data["voice"] = voice
    headers = {
        "Content-Type": "application/json"
    }
    resp = requests.post(url, json=json_data, headers=headers)

    content_type = resp.headers.get("Content-Type")
    if "audio/mpeg" == content_type:

        return resp.content
    else:
        Loo.err(f"request_sound_api_error:{resp.status_code}:{ resp.text}")
        return None
    pass


def create_sound_from_aliyun(text: str, voice: str = None, format: str = "wav", volume: int = 80, speech_rate: int = 0):

    from main import settings

    token = CacheHelper.get(CacheHelper.voice_token)
    if token is None:
        token = get_token(settings.ACCESS_KEY_ID, settings.ACCESS_KEY_SECRET)
        CacheHelper.setForExpire(CacheHelper.voice_token, token, 10)
    sound_app_key = settings.SOUND_APP_KEY
    content = request_sound_api(sound_app_key=sound_app_key, token=token, text=text,
                                voice=voice, format=format, volume=volume, speech_rate=speech_rate)

    if content is None:
        return None
    save_path = default_storage.save(f"any.{format}", io.BytesIO(content))
    # print(aa)
    url = f"http://{settings.BUCKET_NAME}.{settings.END_POINT}/{save_path}"

    return url
    pass
