
import math
from PIL import Image


def GetImageSize(image_fd):
    image = Image.open(image_fd)

    return image.size


'''
这个函数首先计算原始图片的面积，然后将最大面积与原始面积进行比较。
如果原始面积小于等于最大面积，则直接返回原始尺寸。否则，按比例缩小图片，缩小的比例由原始面积与最大面积的比值计算得出。
如果缩小后的图片面积仍然大于最大面积，则将其再次按比例缩小，缩小的比例由缩小后的面积与最大面积的比值计算。最后返回新的图片宽和高。
'''


def optimize_image_size(width, height):
    max_area = 4000000  # 最大面积
    current_area = width * height
    ratio = current_area / max_area  # 计算比例因子
    if current_area <= max_area:
        return width, height
    else:
        new_width = int(width / math.sqrt(ratio))
        new_height = int(height / math.sqrt(ratio))
        new_area = new_width * new_height
        if new_area > max_area:
            new_width = int(new_width / math.sqrt(new_area / max_area))
            new_height = int(new_height / math.sqrt(new_area / max_area))
        return new_width, new_height
