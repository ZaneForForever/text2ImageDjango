

import datetime
import json
from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest


from ai.models.api_key import ApiKey, PlatformEngine
from util.loo import Loo
from voice import aliyun_voice_api, voice_cache
from voice.models import VoiceCreateRecord, VoiceTypeModel, VoiceTypeUserCustomModel
from wx.models.ai_permission import AiPermission, PermissionType
from wx.models.permission_request import PermissionRequest
from ai.models.article import ArticleModel
from ai.models.ai_image_record import ImageCreateRecord
from django.template.loader import render_to_string
#  import make_safe
from django.utils.safestring import mark_safe

def registerAdmin():
    print(__file__ + "引入成功")


@admin.register(VoiceTypeModel)
class VoiceTypeModelAdmin(admin.ModelAdmin):
    list_display = ["id", "display_avatar","name", "voice_id", "class_name",
                    "adapt_scense", "adapt_language", "is_adatpt_er", "updated_at"]

    readonly_fields = ["deleted_at", "created_at", "updated_at"]

    def save_model(self, request: Any, obj: VoiceTypeModel, form: Any, change: Any) -> None:

        if obj.example_voice is None or obj.example_voice == "":
            example_text = f"你好，我是{obj.name}，很高兴认识你，我的声音值得被你选择。"
            #
            obj.example_voice = aliyun_voice_api.create_sound_from_aliyun(
                text=example_text, voice=obj.voice_id)

            pass

        voice_cache.clear_cache(False, obj.voice_id)

        return super().save_model(request, obj, form, change)

    actions = ["clear_cache"]
    
    
    @admin.action(description='清除缓存')
    def clear_cache(self, request: HttpRequest, queryset: QuerySet):
        for obj in queryset:
            voice_cache.clear_cache(False, obj.voice_id)
            pass
        messages.add_message(request, messages.INFO, '清除缓存成功')
        pass
    
    @admin.display(description='头像')
    def display_avatar(self, obj):
        r= f'<img src="{obj.avatar.url}" style="width: 50px; height: 50px; border-radius: 50%;" />'
        return mark_safe(r)


@admin.register(VoiceTypeUserCustomModel)
class VoiceUserCustomAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "voice_id", "wx_user", "updated_at"]
    readonly_fields = ["deleted_at", "created_at", "updated_at"]

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:

        voice_cache.clear_cache(True, obj.voice_id)

        return super().save_model(request, obj, form, change)
    pass


@admin.register(VoiceCreateRecord)
class VoiceRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "voice_id", "wx_user", "created_at"]
    readonly_fields = ["deleted_at", "created_at", "updated_at"]
    pass
