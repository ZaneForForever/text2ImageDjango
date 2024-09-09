

import datetime
import hashlib
import io
import os
from typing import Any
from django.conf import settings
from django.http import JsonResponse
import requests
import base64
import json
from ai.oss.oss_storage import AIImageStorage
from main import settings
import os
import requests
from ai.models.ai_image_record import ImageCreateRecord

from ai.models.api_key import ApiKey
from django.core.files.storage import default_storage

from util.loo import Loo
from util import image_util


def account(api_key=None):
    if api_key is None:
        api_key = ApiKey.objects.filter(
            platform=ApiKey.PLATFORM_STABILITY_AI).first().key

    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    url = f"{api_host}/v1/user/account"
    # if balance:
    # url = f"{api_host}/v1/user/balance"

    if api_key is None:
        raise Exception("Missing Stability API key.")

    response = requests.get(url, headers={
        "Authorization": f"Bearer {api_key}"
    })

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    # Do something with the payload...
    payload = response.json()

    return payload


def query_balance(api_key):
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')

    url = f"{api_host}/v1/user/balance"

    response = requests.get(url, headers={
        "Authorization": f"Bearer {api_key}"
    })

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    # Do something with the payload...
    payload = response.json()

    return payload["credits"]


def query_platform_engines(api_key):
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')

    url = f"{api_host}/v1/engines/list"

    response = requests.get(url, headers={
        "Authorization": f"Bearer {api_key}"
    })

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    # Do something with the payload...
    payload = response.json()

    return payload


def parse_data_save_images(r: ImageCreateRecord, data, user_id,):
    result = []

    result = []
    for i, image in enumerate(data["artifacts"]):
        file_content = base64.b64decode(image["base64"])

        host = f"http://{ settings.BUCKET_NAME}.{settings.END_POINT}"
        save_path = default_storage.save("any.png", io.BytesIO(file_content))
        result.append(f"{host}/{save_path}")

        r.result_width, r.result_height = image_util.GetImageSize(
            io.BytesIO(file_content))
    return result


def text_2_image_v2(r: ImageCreateRecord, user_id: int, api_key: str,  engine_id: str, text_prompts: list, samples: int = 1, style_preset: str = None, width: int = 512, height: int = 512):
    return text_2_image(r, user_id=user_id, api_key=api_key, engine_id=engine_id, text_prompts=text_prompts, samples=samples, style_preset=style_preset, steps=30, cfg_scale=7, width=width, height=height)


def text_2_image(r: ImageCreateRecord, user_id: int, api_key: str, text_prompts: list,  engine_id: str, width: int = 512, height: int = 512, samples: int = 1, steps: int = 30, style_preset: str = None, cfg_scale: int = 7):
    import os
    import requests

    # engine_id = "stable-diffusion-v1-5"
    # engine_id = "stable-diffusion-512-v2-0"
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    post_data = {
        "text_prompts": text_prompts,
        "cfg_scale": cfg_scale,
        "clip_guidance_preset": "FAST_BLUE",
        "height": height,
        "width": width,
        "samples": samples,
        "steps": steps,
    }

    if style_preset:
        post_data['style_preset'] = style_preset

    # print(f"post_data: {post_data}")

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json=post_data,

    )

    r.request_text = json.dumps(post_data)
    r.save()
    if response.status_code != 200:
        r.create_status = ImageCreateRecord.STATUS_API_ERROR
        r.response_text = f"{response.status_code} {response.text}"
        # print(f"Non-200 response: {response.status_code} " + str(response.text))
        raise Exception("Non-200 response: " + str(response.text))

    r.save()

    return parse_data_save_images(r, data=response.json(), user_id=user_id)


def image_2_image_v2(r: ImageCreateRecord, user_id: int, api_key: str,  engine_id: str, extra_image: str, width: int, height: int, text_prompt: str, samples: int = 1, style_preset: str = None):
    if extra_image.startswith("http"):
        oss_url = f"http://{settings.BUCKET_NAME}.{settings.END_POINT}/"

        extra_image = extra_image.replace(
            "https://", "http://").replace(oss_url, "")

        try:

            source_image_fd = default_storage.open(extra_image)
        except Exception as e:

            download_url = f"{oss_url}{extra_image}"

            source_image_fd = requests.get(download_url).content

    else:
        source_image_fd = open(extra_image[1:], "rb")

    return image_2_image(r, user_id=user_id, api_key=api_key, engine_id=engine_id, source_image_fd=source_image_fd, text_prompt=text_prompt, samples=samples, style_preset=style_preset, width=width, height=height, steps=30, cfg_scale=7)
    pass


def image_2_image(r: ImageCreateRecord, source_image_fd, api_key: str,   user_id, text_prompt: str, engine_id: str,  style_preset: str = None,  image_strength=None, width: int = 512, height: int = 512, samples: int = 1, steps=None, cfg_scale=None):

    if steps is None:
        # Default50 [10~150]
        steps = 50
    if image_strength is None:
        #  default=0.35 [0~1]
        image_strength = 0.35

    if cfg_scale is None:
        # default=7 [0~35]
        cfg_scale = 30

    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    # print(f"image_2_image: {source_image}")

    post_data = {
        "init_image_mode": "IMAGE_STRENGTH",
        "image_strength": image_strength,
        "text_prompts[0][text]": text_prompt,
        "clip_guidance_preset": "FAST_BLUE",
        "samples": samples,
        "cfg_scale": cfg_scale,

        "steps": steps,
    }

    if style_preset:
        post_data['style_preset'] = style_preset

    Loo.err(f"image_2_image: {post_data}------ ")

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/image-to-image",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        files={
            "init_image": source_image_fd
        },
        data=post_data,

    )
    r.request_text = json.dumps(post_data)
    r.save()

    # Loo.err(f"image_2_image: {response.status_code} " + str(response.text))

    if response.status_code != 200:
        Loo.err(
            f"Non-200 response: {response.status_code} " + str(response.text))
        raise Exception(
            f"Non-200 response:{response.status_code} " + str(response.text))

    r.response_text = "成功，不要在意数据，图片全部都在数据里,很庞大"
    r.save()

    return parse_data_save_images(r, data=response.json(), user_id=user_id)


def UpscaleImage(r: ImageCreateRecord,  api_key: str, width: int, height: int, engine_id: str = "stable-diffusion-x4-latent-upscaler",):
    import json
    api_host = os.getenv("API_HOST", "https://api.stability.ai")

    post_data = {
        # "width": 2048,
        # "height": 2048,
    }

    if width >= height:
        post_data["width"] = 2048
    else:
        post_data["height"] = 2048
        pass
    url = f"{api_host}/v1/generation/{engine_id}/image-to-image/upscale"

    img_resp = requests.get(r.extra_image)
    img_resp_content_type = img_resp.headers.get('Content-Type')

    # print(width, height)

    # print(post_data)

    response = requests.post(
        url,
        headers={
            "Accept": "image/png",
            "Authorization": f"Bearer {api_key}"
        },
        files={
            "image": ("a.png", img_resp.content, img_resp_content_type)
        },
        data=post_data
    )

    r.request_text = json.dumps({
        "post_data": post_data,
        "url": url,
    })
    r.save()

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))
    # print(response.content)
    save_path = default_storage.save(f"any.png", io.BytesIO(response.content))
    # print(aa)
    url = f"http://{settings.BUCKET_NAME}.{settings.END_POINT}/{save_path}"
    return [url]
