

import datetime
from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from ai.models.crontab_record import CrontabCreateImage, CrontabRecord
from ai.third import stability_ai

from ai.models.api_key import ApiKey, PlatformEngine
from wx.models.ai_permission import AiPermission, PermissionType
from wx.models.permission_request import PermissionRequest


def registerAdmin():
    print(__file__ + "引入成功")


class CrontabImageInline(admin.TabularInline):
    model = CrontabCreateImage
    # list_display = ["id", "image_id", "crontab_record_id"]
    fields = ["create_image__id","create_image__wx_user"]
    can_delete = False
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('create_image')  # 预先加载Author模型
        qs = qs.annotate(gender=F('create_image__id'), region=F(
            'create_image__wx_user'))  # 将Author模型中的字段加入到BookAuthor模型中
        return qs


@admin.register(CrontabRecord)
class CrontabRecordAdmin(admin.ModelAdmin):
    # inlines = [CrontabImageInline]

    list_display = ["id",  "crontab_minute",
                    "crontab_times", "created_at", "end_time"]
    pass
