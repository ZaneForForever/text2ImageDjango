import io
import math
from PIL import Image
from ai.models.ai_image_record import ImageCreateRecord


from util.number_util import NumberUtil


import io
from PIL import Image
import requests


def GetOrderingImageTask() -> ImageCreateRecord:

    return ImageCreateRecord.objects.filter(create_status=ImageCreateRecord.STATUS_ORDERING).order_by("-id").first()

    # return None


def GetImageFromUrl(url: str):
    if not url or len(url) <= 0:
        return None
    if not url.startswith("http"):
        return None
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    return resp.content


def convertImage(f_read):
    # 读取图片并获取其尺寸

    img = Image.open(f_read)
    width, height = img.size

    # 缩放图片使得其宽和高都是64的倍数并且小于512*512
    new_width = (width // 64) * 64
    new_height = (height // 64) * 64
    if new_width > 512 or new_height > 512:
        scale_factor = min(512 / new_width, 512 / new_height)
        new_width = int(new_width * scale_factor)
        new_height = int(new_height * scale_factor)

    new_width = NumberUtil.find_nearest_multiple(new_width, 64)
    new_height = NumberUtil.find_nearest_multiple(new_height, 64)

    img = img.resize((new_width, new_height), resample=Image.BICUBIC)

    # 将图片存储为内存流
    stream = io.BytesIO()
    img.save(stream, format='PNG')
    stream.seek(0)

    return stream
