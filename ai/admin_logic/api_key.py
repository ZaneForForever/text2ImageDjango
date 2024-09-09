

import datetime
from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from ai.third import stability_ai

from ai.models.api_key import ApiKey, PlatformEngine
from wx.models.ai_permission import AiPermission, PermissionType
from wx.models.permission_request import PermissionRequest


def registerAdmin():
    print(__file__ + "引入成功")


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):

    list_display = ("id", "platform", "last_use_time", "use_times",
                    "name", "balance", "available")

    readonly_fields = ('deleted_at',)

    @admin.display(description='余额')
    def balance(self, obj):
        # if obj.platform == 1:
        #     return stability_ai.query_balance(obj.key)
        return "-"


@admin.register(PlatformEngine)
class PlatformEngineAdmin(admin.ModelAdmin):

    list_display = ("platform_engine_id", "id", "platform", "type_name", "is_upscale", "sort",
                    "remark", "available")

    readonly_fields = ('deleted_at',)

    list_editable = ["available", "is_upscale", "sort",]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        result = super().get_queryset(request)
        # last_update_time = PlatformEngine.objects.filter(
        #     platform=1).first() .updated_at
        # if (datetime.datetime.now(tz=pytz.UTC) - last_update_time) > datetime.timedelta(minutes=5):
        #     return result

        #  stability ai
        engines_list = stability_ai.query_platform_engines(
            ApiKey.objects.filter(platform=1).first().key)

        ids = []
        for e in engines_list:

            e_obj, is_new = PlatformEngine.objects.get_or_create(
                platform=1,
                platform_engine_id=e["id"],

            )
            e_obj.remark = e["description"]
            e_obj.type_name = e["type"]
            e_obj.deleted_at = None
            e_obj.save()

            ids.append(e_obj.id)

        #  删除已经不可用的引擎
        PlatformEngine.objects.filter(platform=1).exclude(
            id__in=ids).update(deleted_at=datetime.datetime.now(), available=False)

        return result
