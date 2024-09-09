

from django.http import HttpRequest, JsonResponse
from ai.models.platform_settings import PlatformSettingModel

from ai.models.post_params_config import ParamsFieldModel

from ai.cache.cache_helper import CacheHelper


def GetTabIcons(request: HttpRequest):

    cache = CacheHelper.get(CacheHelper.key_tab_icons)
    if cache is not None:

        return JsonResponse({"code": 0, "msg": "ok", "data": cache})

    icons = []

    for i in PlatformSettingModel.objects.filter(id__gte=0).order_by("sort"):
        if i.code.startswith("tab_icon"):
            icons.append(i.value_str)
            pass
        pass

    CacheHelper.set(CacheHelper.key_tab_icons, icons)

    return JsonResponse({"code": 0, "data": icons}, safe=False)


def GetConfigParams(request):

    # cache = CacheHelper.get(CacheHelper.platform_config_params)
    # if cache is not None:

    #     return JsonResponse({"code": 0, "msg": "ok", "data": cache})
    configs = []
    for p in ParamsFieldModel.objects.filter(available=True).order_by("is_advanced", "order"):
        configs.append(p.ToJson())
        pass
    CacheHelper.set(CacheHelper.platform_config_params, configs)
    return JsonResponse({"code": 0, "msg": "ok", "data": configs})
