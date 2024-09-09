

from django.http import HttpRequest, JsonResponse
from voice import aliyun_voice_api
from voice.models import VoiceCreateRecord, VoiceTypeModel, VoiceTypeUserCustomModel


from util.django_request_decorator import check_user_ai_permission, convert_form_data_2_get_params, convert_post_json_2_get_params, convert_session_to_wx_user
from django.views.decorators.csrf import csrf_exempt
from wx.models.ai_permission import PermissionType


@csrf_exempt
@convert_post_json_2_get_params(required_fields=["session", "text", "voice_id", "use_custom"])
@convert_session_to_wx_user
@check_user_ai_permission(PermissionType.AI_IMAGE)
def text2Voice(request: HttpRequest):
    text = request.GET.get("text")

    voice_id = request.GET.get("voice_id")

    wx_user = request.GET.get("wx_user")

    if request.GET.get("use_custom") == True:
        custom_voice = VoiceTypeUserCustomModel.objects.filter(
            wx_user=wx_user).first()
        if custom_voice is None:
            return JsonResponse({"code": 1, "msg": "没有自定义语音"})
        pass

    # voice: VoiceTypeModel = VoiceTypeModel.objects.filter(voice_id=voice_id).first()
    # if voice is None:
    #     return JsonResponse({"code": 1, "msg": "voice_id错误"})

    speech_rate = int(request.GET.get("speech_rate", 0))
    url = aliyun_voice_api.create_sound_from_aliyun(
        text=text, voice=voice_id, speech_rate=speech_rate*100)
    if url is None:
        return JsonResponse({"code": 1, "msg": "生成语音失败"})

    user = request.GET.get("wx_user")

    r = VoiceCreateRecord()
    r.wx_user = user
    r.text = text
    r.voice_id = voice_id
    r.voice_url = url
    r.speech_rate = speech_rate
    r.save()
    return JsonResponse({"code": 0, "msg": "", "data": {"text": text, "url": url}})
    pass


@csrf_exempt
@convert_post_json_2_get_params(required_fields=["session"])
@convert_session_to_wx_user
@check_user_ai_permission(PermissionType.AI_IMAGE)
def VoiceTypeList(request: HttpRequest):
    voice_list = []
    q = VoiceTypeModel.objects.filter(
        deleted_at__isnull=True).order_by('sort')[0:1000]
    for v in q:
        voice_list.append(v.ToJsonObj())

    custom_voice_list = []
    # 获取用户自定义的语音
    wx_user = request.GET.get("wx_user")
    custom_voice_list = [i.ToJsonObj()
                         for i in VoiceTypeUserCustomModel.objects.filter(wx_user=wx_user)]
    return JsonResponse({"code": 0, "msg": "", "data": {"custom_voice_list": custom_voice_list, "voice_list": voice_list, }})
    pass


@csrf_exempt
@convert_post_json_2_get_params(required_fields=["session", "offset", "count"])
@convert_session_to_wx_user
@check_user_ai_permission(PermissionType.AI_IMAGE)
def UserVoiceRecords(request: HttpRequest):
    user = request.GET.get("wx_user")
    offset = int(request.GET.get("offset"))
    count = int(request.GET.get("count"))
    q = VoiceCreateRecord.objects.filter(
        wx_user=user, deleted_at__isnull=True).order_by('-created_at')[offset:offset+count]
    records = []
    for r in q:
        records.append(r.ToJsonObj())
    return JsonResponse({"code": 0, "msg": "", "data": {"records": records}})
    pass
