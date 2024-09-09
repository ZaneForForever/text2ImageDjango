
import datetime
import io
import os
import PIL
from django.core.files.storage import default_storage
from django.http import JsonResponse
from ai.api import image_service
from ai.models.record_upload_image import RecordUploadImage
from util.django_request_decorator import check_user_ai_permission, convert_form_data_2_get_params, convert_post_json_2_get_params, convert_session_to_wx_user
from util.loo import Loo
from wx.models.ai_permission import PermissionType

from wx.models.wx_user_model import WxUser

from django.views.decorators.csrf import csrf_exempt
from util import image_util


@csrf_exempt
@convert_form_data_2_get_params(required_fields=["session"])
@convert_session_to_wx_user
@check_user_ai_permission(PermissionType.AI_IMAGE)
def UploadImage(request):
    user = request.GET.get("wx_user")

    if request.method == "GET":
        Loo.error(f"{user}-请使用POST方法上传图片")
        return JsonResponse({"code": 1, "msg": "请使用POST方法上传图片"})

    data = dict()

    file_list = request.FILES.getlist('file')
    file = file_list[0]
    
    source_buffer= io.BytesIO(file.read())


    source_width, source_height = image_util.GetImageSize(file)
    if source_width < 128 or source_height < 128:
        Loo.error(f"{user}-图片太小了")
        return JsonResponse({"code": 1, "msg": "图片太小了"})

    parent_path = f"{user.id}"

    os.makedirs(parent_path) if not os.path.exists(parent_path) else None

    file_type_name = file.name.split('.')[-1]

    ru: RecordUploadImage = RecordUploadImage(wx_user=user)

    source_image_save_path = f"{parent_path}/{datetime.datetime.now().timestamp()}_big.{file_type_name}"
    scale_image_save_path = f"{parent_path}/{datetime.datetime.now().timestamp()}_small.{file_type_name}"

    ru.source_width, ru.source_height = image_util.GetImageSize(file)

    scale_file = image_service.convertImage(file)

    ru.scale_width, ru.scale_height = image_util.GetImageSize(scale_file)

    
    
    ru.source_image.save(source_image_save_path,source_buffer)
    ru.scale_image.save(scale_image_save_path, scale_file)

    ru.save()

    data = {
        "url": ru.scale_image.url,

        # "path": ru.scale_image.path,

    }
    # print(data)

    return JsonResponse({"code": 0, "data": data})
