

import datetime
import json
from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest


from ai.models.api_key import ApiKey, PlatformEngine
from wx.models.ai_permission import AiPermission, PermissionType
from wx.models.permission_request import PermissionRequest
from ai.models.article import ArticleModel
from ai.models.ai_image_record import ImageCreateRecord
from django.template.loader import render_to_string


def registerAdmin():
    print(__file__ + "引入成功")


@admin.register(ArticleModel)
class ArticleModelAdmin(admin.ModelAdmin):
    list_display = ["id", "wx_user", "title","image_id","image_create_record_display",
                    "created_at", "updated_at"]
    
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')

    @admin.display(description='图片记录id')
    def image_id(self, o):
        if o.image_create_record is None:
            return ""
        return o.image_create_record.id
    
    @admin.display(description='图片记录')
    def image_create_record_display(self, o):
        if o.image_create_record is None:
            return ""

        obj: ImageCreateRecord = o.image_create_record

        if obj.images is None or obj.images == "" or obj.big_images is None or len(obj.big_images) == 0:
            return ""
        images = json.loads(obj.images)
        big_images = json.loads(obj.big_images)

        image_urls = []
        for i in range(0, len(images)):

            host = f"http://{obj.request_host}" if obj.is_local(
            ) else "http://go.ai.tianshuo.vip"

            image_urls.append(
                {"url": host+images[i], "big_url": host+big_images[i]})

        return render_to_string("ai/list_field/images.html", {"images": image_urls, "task": obj, "width": 600})

    pass
