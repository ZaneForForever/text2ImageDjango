

from django.http import HttpRequest, JsonResponse

from ai.models.ai_image_record import ImageCreateRecord
from ai.models.api_key import ApiKey


def getWaitTask():
    r: ImageCreateRecord = ImageCreateRecord.objects.filter(
        api_platform_type=ApiKey.PLATFORM_SD_WEB_UI_API).filter(create_status=ImageCreateRecord.STATUS_API_PROCESSING).first()
    if r:
        r.create_status = ImageCreateRecord.STATUS_ORDERING
        # r.save()

    return r

def getUpsaleTasks():
    r: ImageCreateRecord = ImageCreateRecord.objects.filter(
        api_platform_type=ApiKey.PLATFORM_SD_WEB_UI_API).filter(create_status=ImageCreateRecord.STATUS_API_PROCESSING).first()
    if r:
        r.create_status = ImageCreateRecord.STATUS_ORDERING
        # r.save()
    return r

def getSdWebUiTasks(request: HttpRequest):
    r: ImageCreateRecord = getWaitTask()
    return JsonResponse({"code": 0, "data": r.ToJsonObj() if r else None})
