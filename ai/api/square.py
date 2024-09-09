

from django.http import HttpRequest, JsonResponse
from ai.models.ai_image_record import ImageCreateRecord
from ai.models.article import ArticleModel
from ai.models.prompt_example import PromptExampleImageModel
from util.number_util import NumberUtil

from wx.models.ai_permission import PermissionType
from util.django_request_decorator import check_user_ai_permission, convert_post_json_2_get_params, convert_session_to_wx_user
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@convert_post_json_2_get_params(required_fields=["session"])
@convert_session_to_wx_user
def GetPromptExample(request: HttpRequest):
    q = PromptExampleImageModel.objects.filter(
        deleted_at__isnull=True).order_by('-id')[0:100]
    random_index = NumberUtil.random_int(0, len(q)-1)
    p = q[random_index]
    return JsonResponse({"code": 0, "data": {"prompt": p.create_image_record.source_prompt_text}})


@csrf_exempt
@convert_post_json_2_get_params(required_fields=["session", "record_id"])
@convert_session_to_wx_user
@check_user_ai_permission(permission_name=PermissionType.AI_IMAGE)
def PublishImage(request: HttpRequest):

    r: ImageCreateRecord = ImageCreateRecord.objects.filter(
        id=request.GET.get("record_id")).first()
    if r is None:
        return JsonResponse({"code": 1, "msg": "没有找到uuid记录"})
    if r.wx_user != request.GET.get("wx_user"):
        return JsonResponse({"code": 1, "msg": "不是你的图片"})

    r.is_published = True
    r.save()

    a: ArticleModel = ArticleModel.objects.get_or_create(image_create_record_id=r.id)[
        0]

    a.wx_user = r.wx_user

    if r.create_type == ImageCreateRecord.IMAGE_UPSCALE:
        a.title = "高清精绘"
    else:
        a.title = r.source_prompt_text

    a.save()

    return JsonResponse({"code": 0, "data": a.ToJsonObj()})


@csrf_exempt
@convert_post_json_2_get_params(required_fields=["session"])
@convert_session_to_wx_user
@check_user_ai_permission(permission_name=PermissionType.AI_IMAGE)
def SquareList(request: HttpRequest):
    offset = request.GET.get("offset", 0)
    count = request.GET.get("count", 10)
    data = ArticleModel.objects.filter(
        deleted_at__isnull=True).order_by('-id')[offset:offset+count]
    data = [i.ToJsonObj() for i in data]
    return JsonResponse({"code": 0, "data": data})
