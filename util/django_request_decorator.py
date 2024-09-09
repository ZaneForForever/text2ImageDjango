from functools import wraps
import json

from django.http import HttpRequest, JsonResponse
from main import settings
from requestStat.service import RequestStatService
from util.loo import Loo
from wx.models.ai_permission import PermissionType

from wx.models.wx_user_model import WxUser


def convert_form_data_2_get_params(required_fields=[]):
    def wrapper(view_func):
        @wraps(view_func)
        def inner(request, *args, **kwargs):
            if request.method == "POST":
                request.GET._mutable = True
                for key in request.POST:
                    request.GET[key] = request.POST[key]

            
            
            for required_field in required_fields:
                if request.GET.get(required_field) is None:
                    return JsonResponse({"code": 1, "msg": f"缺少参数{required_field}"})
                pass

            if settings.is_online():
                try:
                    return view_func(request, *args, **kwargs)
                except Exception as e:
                    Loo.error(e)
                    return JsonResponse({"code": 1, "msg": "服务器错误"})
            else:
                return view_func(request, *args, **kwargs)

        return inner
    return wrapper


def convert_post_json_2_get_params(required_fields=[]):
    def wrapper(view_func):
        @wraps(view_func)
        def inner(request, *args, **kwargs):
            if request.method == "POST" and len(request.body) > 0:
                request.GET._mutable = True
                body = request.body.decode("utf-8")
                request_json_dict = json.loads(body)
                for key in request_json_dict:
                    request.GET[key] = request_json_dict[key]

            for required_field in required_fields:
                if request.GET.get(required_field) is None:
                    return JsonResponse({"code": 1, "msg": f"缺少参数{required_field}"})
                pass

            return view_func(request, *args, **kwargs)
        return inner
    return wrapper


def convert_session_to_wx_user(method, *args, **kwargs):
    def sam(*args, **kw):
        request: HttpRequest = args[0]
        session = request.GET.get("session", None)
        if session is None or len(session) == 0:
            return JsonResponse({"code": 1, "msg": "session不能为空"})

        user: WxUser = None
        try:
            user = WxUser.objects.get(session=session)
        except WxUser.DoesNotExist:
            pass
        if user is None:
            return JsonResponse({"code": 1, "msg": "session无效"})
        else:
            request.GET._mutable = True
            request.GET["wx_user"] = user

            try:
                RequestStatService.add_request_stat(user.id, request)
            except:
                Loo.error("记录请求统计失败")
                pass
        return method(*args, **kw)

    return sam


def check_user_ai_permission(permission_name):
    def wrapper(view_func):
        @wraps(view_func)
        def inner(request, *args, **kwargs):
            user = request.GET.get("wx_user", None)
            if user is None:
                session = request.GET.get("session", None)
                if session is None or len(session) == 0:
                    return JsonResponse({"code": 1, "msg": "session不能为空"})
                user: WxUser = None
                try:
                    user = WxUser.objects.get(session=session)
                    request.GET["wx_user"] = user
                except WxUser.DoesNotExist:
                    pass

            if user is not None and user.has_permission(permission_name) is False:
                return JsonResponse({"code": 1, "msg": "没有AI画图权限"})
            return view_func(request, *args, **kwargs)
        return inner
    return wrapper
