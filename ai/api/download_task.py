

import datetime
import hashlib
import io
import json
import os
from django.http import HttpResponse, JsonResponse
from ai.models.ai_image_record import ImageCreateRecord

from ai.models.download_task import DownloadTask
from django.views.decorators.csrf import csrf_exempt
from main import settings

from PIL import Image


@csrf_exempt
def download_tasks(request):

    task: DownloadTask = DownloadTask.objects.filter(
        download_status=DownloadTask.STATUS_INIT).filter(from_url__isnull=False).exclude(from_url='').first()
    if task is None:
        # 取不到就取失败的列表
        task = DownloadTask.objects.filter(
            download_status=DownloadTask.STATUS_FAILED).filter(from_url__isnull=False).exclude(from_url='').first()
        if task is None:
            return JsonResponse({"code": 1, "msg": "没有任务"})

    task.download_status = DownloadTask.STATUS_DOWNLOADING
    task.save()
    return JsonResponse({
        "code": 0,
        "task": task.ToJsonObj()
    }, safe=False)


def on_download_finish_v2(task: DownloadTask,  record: ImageCreateRecord, fileContent,):
    from PIL import Image
    user_id = record.wx_user.id

    current_month = datetime.datetime.now().strftime("%Y%m")

    save_dir = f"{current_month}"

    file_md5 = hashlib.md5(fileContent).hexdigest()

    task.save_path = f"{save_dir}/task_{file_md5}.png"

    record.result_width, record.result_height, small_save_paths, big_save_paths = crop4ImagesAndSaveV2(
        io.BytesIO(fileContent), task, user_id)

    task.save_path = json.dumps({
        "small": small_save_paths,
        "big": big_save_paths
    })
    host = f"http://{settings.BUCKET_NAME}.{settings.END_POINT}"
    record.images = json.dumps([f"{host}/{i}"for i in small_save_paths])

    record.big_images = json.dumps([f"{host}/{i}"for i in big_save_paths])
    first_image = big_save_paths[0]
    print(record.images)
    print(record.big_images)

    # record.result_width, record.result_height = Image.open(first_image).size

    # record.images = saleImages(crop_images_path,task.save_path, task, user_id)

    record.create_status = ImageCreateRecord.STATUS_SUCCESS
    task.download_status = DownloadTask.STATUS_SUCCESS

    record.updated_at = datetime.datetime.now()
    record.save()
    task.updated_at = datetime.datetime.now()
    task.save()
    pass


def on_download_finish(task: DownloadTask,  record: ImageCreateRecord, fileContent,):
    from PIL import Image
    user_id = record.wx_user.id

    save_dir = f"media/{user_id}/out"

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    task.save_path = f"{save_dir}/task_{task.id}.png"

    with open(task.save_path, "wb") as f:
        f.write(fileContent)

    small_save_paths, big_save_paths = crop4ImagesAndSave(
        task.save_path, task, user_id)

    task.save_path = json.dumps({
        "small": small_save_paths,
        "big": big_save_paths
    })

    record.images = json.dumps([f"/{i}"for i in small_save_paths])

    record.big_images = json.dumps([f"/{i}"for i in big_save_paths])
    first_image = big_save_paths[0]

    record.result_width, record.result_height = Image.open(first_image).size

    # record.images = saleImages(crop_images_path,task.save_path, task, user_id)

    record.create_status = ImageCreateRecord.STATUS_SUCCESS
    task.download_status = DownloadTask.STATUS_SUCCESS

    record.updated_at = datetime.datetime.now()
    record.save()
    task.updated_at = datetime.datetime.now()
    task.save()
    pass


@csrf_exempt
def download_finish(request):

    # task_id = request.GET.get("taskId")

    # task = DownloadTask.objects.get(id=task_id)
    # record: ImageCreateRecord = task.image_create_record

    # file = request.FILES['file'].read()

    # on_download_finish(task, file, record)

    # return JsonResponse({"code": 0, "msg": "ok", "data": record.ToJsonObj()})
    return JsonResponse({"code": 999, "msg": "un used"})


def saleImages(images, path, task, user_id):
    for i in images:
        big_image = Image.open(i)
        width, height = big_image.size
        to_width = 400
        to_height = int((height/width)*to_width)

        resize_image = big_image.resize((to_width, to_height), Image.ANTIALIAS)

        resize_image.save(i)
        pass
    pass


@csrf_exempt
def download_failed(request):
    task_id = request.GET.get("taskId")
    task = DownloadTask.objects.get(id=task_id)
    task.download_status = DownloadTask.STATUS_FAILED
    task.save()
    return JsonResponse({"code": 0, "msg": "ok"})


def crop4ImagesAndSave(fp, task: DownloadTask, user_id: int):
    # 打开大图
    big_image = Image.open(fp)

    # 获取大图尺寸
    width, height = big_image.size

    # 计算每个小图的尺寸
    small_width = width // 2
    small_height = height // 2

    # 依次截取四个小图
    top_left = big_image.crop((0, 0, small_width, small_height))
    top_right = big_image.crop((small_width, 0, width, small_height))
    bottom_left = big_image.crop((0, small_height, small_width, height))
    bottom_right = big_image.crop((small_width, small_height, width, height))

    suffix_path = f"media/{user_id}/out/task"

    to_width = 400
    to_height = int((height/width)*to_width)

    top_left_small = top_left.resize((to_width, to_height), Image.ANTIALIAS)
    top_right_small = top_right.resize((to_width, to_height), Image.ANTIALIAS)
    bottom_left_small = bottom_left.resize(
        (to_width, to_height), Image.ANTIALIAS)
    bottom_right_small = bottom_right.resize(
        (to_width, to_height), Image.ANTIALIAS)

    p1 = f"{suffix_path}{task.id}_1.png"
    p2 = f"{suffix_path}{task.id}_2.png"
    p3 = f"{suffix_path}{task.id}_3.png"
    p4 = f"{suffix_path}{task.id}_4.png"

    top_left_small.save(p1)
    top_right_small.save(p2)
    bottom_left_small.save(p3)
    bottom_right_small.save(p4)

    big_p1 = f"{suffix_path}{task.id}_big_1.png"
    big_p2 = f"{suffix_path}{task.id}_big_2.png"
    big_p3 = f"{suffix_path}{task.id}_big_3.png"
    big_p4 = f"{suffix_path}{task.id}_big_4.png"

    top_left.save(big_p1)
    top_right.save(big_p2)
    bottom_left.save(big_p3)
    bottom_right.save(big_p4)

    return [p1, p2, p3, p4], [big_p1, big_p2, big_p3, big_p4]


def save_2_oss(img):
    from django.core.files.storage import default_storage
    p1_io = io.BytesIO()
    img.save(p1_io, format='PNG')
    p1_io.seek(0)
    p1 = default_storage.save(f"any.png", p1_io)
    return p1


def crop4ImagesAndSaveV2(fp, task: DownloadTask, user_id: int):
    # 打开大图
    big_image = Image.open(fp)

    # 获取大图尺寸
    width, height = big_image.size

    # 计算每个小图的尺寸
    small_width = width // 2
    small_height = height // 2

    # 依次截取四个小图
    top_left = big_image.crop((0, 0, small_width, small_height))
    top_right = big_image.crop((small_width, 0, width, small_height))
    bottom_left = big_image.crop((0, small_height, small_width, height))
    bottom_right = big_image.crop((small_width, small_height, width, height))

    to_width = 400
    to_height = int((height/width)*to_width)

    top_left_small = top_left.resize((to_width, to_height), Image.ANTIALIAS)
    top_right_small = top_right.resize((to_width, to_height), Image.ANTIALIAS)
    bottom_left_small = bottom_left.resize(
        (to_width, to_height), Image.ANTIALIAS)
    bottom_right_small = bottom_right.resize(
        (to_width, to_height), Image.ANTIALIAS)

    p1 = save_2_oss(top_left_small)
    p2 = save_2_oss(top_right_small)
    p3 = save_2_oss(bottom_left_small)
    p4 = save_2_oss(bottom_right_small)

    big_p1 = save_2_oss(top_left)
    big_p2 = save_2_oss(top_right)
    big_p3 = save_2_oss(bottom_left)
    big_p4 = save_2_oss(bottom_right)

    return small_width, small_height, [p1, p2, p3, p4], [big_p1, big_p2, big_p3, big_p4]
