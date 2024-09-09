

import json
import logging
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ai.models.ai_image_record import ImageCreateRecord
from ai.models.download_task import DownloadTask
from ai.models.webhook_record import WebhookRecord
from ai.multi_progress import download_image_progress
from util.loo import Loo


@csrf_exempt
def zhi_shu_yun_imagine(request: HttpRequest):
    ip = request.headers["X-Real-IP"] if "X-Real-IP" in request.headers else ""
    wr: WebhookRecord = WebhookRecord()
    wr.request_ip = ip
    wr.request_text = request.body
    wr.request_path = request.path
    wr.request_type = "zhishuyun_imagine"

    o = json.loads(request.body)

    if "task_id" not in o or o["task_id"] == "":
        wr.save()
        return HttpResponse("ok")

    wr.originatingMessageId = o["task_id"]
    wr.save()

    if wr.originatingMessageId is None or wr.originatingMessageId == "":
        return HttpResponse("ok")
        pass

    r = ImageCreateRecord.objects.filter(
        message_id=wr.originatingMessageId).first()
    if r is None:
        return HttpResponse("ok")

    r.create_status = ImageCreateRecord.STATUS_WEBHOOK_PROCESSING
    r.save()

    image_url_json_key = "image_url"

    if image_url_json_key in o and o[image_url_json_key] != "" and len(o[image_url_json_key]) > 0:
        image_url = o[image_url_json_key]
        r.images = json.dumps([image_url])
        r.create_status = ImageCreateRecord.STATUS_WEBHOOK_SUCCESS
        r.save()
        task, is_new = DownloadTask.objects.get_or_create(
            image_create_record=r)
        task.download_status = DownloadTask.STATUS_INIT

        task.download_status = DownloadTask.STATUS_DOWNLOADING

        task.from_url = image_url.replace("cdn.discordapp.com", "midjourney.cdn.zhishuyun.com").replace(
            "media.discordapp.net", "midjourney.cdn.zhishuyun.com")
        task.save()

        r.create_status = ImageCreateRecord.STATUS_DOWNLOAD_START
        r.save()

        download_image_progress.download_background(task.id)

    else:
        Loo.info(f"{ip}没有图片{request.body}")
        r.create_status = ImageCreateRecord.STATUS_WEBHOOK_ERROR
        r.save()

    return HttpResponse("ok")


@csrf_exempt
def TheNextLegWebhook(request: HttpRequest):
    # print(request.body)
    # print(request.POST)
    ip = request.headers["X-Real-IP"] if "X-Real-IP" in request.headers else ""

    # loo(f"{ip}{request.body}")

    wr: WebhookRecord = WebhookRecord()
    wr.request_ip = ip
    wr.request_text = request.body
    wr.request_path = request.path
    wr.request_type = "NextLegWebhook"

    o = json.loads(request.body)

    if "originatingMessageId" in o:
        wr.originatingMessageId = o["originatingMessageId"]

        wr.save()

    if "buttonMessageId" in o:
        wr.buttonMessageId = o["buttonMessageId"]

    wr.save()

    r = ImageCreateRecord.objects.filter(
        message_id=wr.originatingMessageId).first()
    if r is None:
        return HttpResponse("ok")

    r.create_status = ImageCreateRecord.STATUS_WEBHOOK_PROCESSING
    r.save()

    if "imageUrl" in o and o["imageUrl"] != "" and len(o["imageUrl"]) > 0:
        image_url = o["imageUrl"]
        r.images = json.dumps([image_url])
        r.create_status = ImageCreateRecord.STATUS_WEBHOOK_SUCCESS
        r.save()
        task, is_new = DownloadTask.objects.get_or_create(
            image_create_record=r)
        task.download_status = DownloadTask.STATUS_INIT

        task.download_status = DownloadTask.STATUS_DOWNLOADING

        task.from_url = image_url
        task.save()

        r.create_status = ImageCreateRecord.STATUS_DOWNLOAD_START
        r.save()

        download_image_progress.download_background(task.id)

    else:
        Loo.info(f"{ip}没有图片{request.body}")
        r.create_status = ImageCreateRecord.STATUS_WEBHOOK_ERROR
        r.save()

    return HttpResponse("ok")
