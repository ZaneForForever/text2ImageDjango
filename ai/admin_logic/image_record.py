

import json
from typing import Any, List, Tuple
from django.contrib import admin
from main import settings

from ai.models.ai_image_record import ImageCreateRecord
from django.template.loader import render_to_string

from ai.models.api_key import ApiKey
from ai.multi_progress import create_images_progress, download_image_progress


def registerAdmin():
    print(__file__ + "引入成功")


class CustomApiKeyPlatformFilter(admin.SimpleListFilter):
    title = "第三方平台"
    parameter_name = 'api_key_platform'

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        return ApiKey.platform_choices

    def queryset(self, request: Any, queryset: Any) -> Any:
        if self.value() is None:
            return queryset
        return queryset.filter(api_key__platform=self.value())


@admin.register(ImageCreateRecord)
class ImageCreateRecordAdmin(admin.ModelAdmin):

    # class Media:
    #     css = {
    #         'js': ('admin-custom/js/show_image_alert.js',)
    #     }

    search_fields = ['uuid', 'wx_user__nickname', 'wx_user__openid']

    list_display = ['id', "uuid", 'api_platform_type', 'request_host', 'create_type', 'source_prompt_text', 'wx_user',  'display_extra_image', 'display_images', "create_duration", 'create_status',
                    'created_at']

    list_filter = (

        CustomApiKeyPlatformFilter,
        'create_type', 'is_async', 'wx_user', 'created_at')

    change_list_template = "admin-custom/ai/image_record_change_list.html"

    readonly_fields = ('created_at', 'updated_at',
                       'deleted_at', 'display_extra_image', 'display_images', 'detail_display_images', 'params')

    fieldsets = (

        ('基础信息', {
            'fields': ('uuid', 'wx_user',  'create_type'),
        }),
        ('prompt信息', {
            'fields': ('source_prompt_text', 'prompt_text', 'params','negative_prompt','source_negative_prompt',),
        }),
        ('图片信息', {
            'fields': ('display_extra_image', 'detail_display_images', ),
        }),

        ('创建信息', {
            'fields': ('create_status', 'api_platform_type', 'is_async'),
        }),

        ('数据交互', {
            'fields': ('request_text', 'response_text', ),
        }),

        ('时间', {'fields': ('created_at', 'updated_at')}),
    )

    pass

    @admin.display(description='参考图')
    def display_extra_image(self, o):
        # o: ImageCreateRecord = self
        if o.extra_image is None or o.extra_image == "":
            return "-"
        host = f"http://{o.request_host}" if o.is_local() else "http://go.ai.tianshuo.vip"
        if o.extra_image.startswith("http"):
            host = ""

        image_urls = [{
            "url": host+o.extra_image,
            "big_url": host+o.extra_image
        }]
        return render_to_string("ai/list_field/images.html", {"images": image_urls, "task": o, "width": 100, "img_width": 100})

    @admin.display(description='图片列表')
    def display_images(self, o):
        return self.show_list_images(o, 600, 100)

    @admin.display(description='详情图片列表')
    def detail_display_images(self, o):
        return self.show_list_images(o, 900, 400)

    def show_list_images(self, obj: ImageCreateRecord, div_width: int = 600, img_width: int = 100):

        if obj.images is None or obj.images == "" or obj.big_images is None or len(obj.big_images) == 0:
            return ""
        images = json.loads(obj.images)
        big_images = json.loads(obj.big_images)

        image_urls = []
        for i in range(0, len(images)):

            if images[i].startswith("http"):
                host = ""
            else:
                host = "http://go.ai.tianshuo.vip"

            image_urls.append(
                {"url": host+images[i], "big_url": host+big_images[i]})

        return render_to_string("ai/list_field/images.html", {"images": image_urls, "task": obj, "width": div_width, "img_width": img_width})

    @admin.display(description='耗时')
    def create_duration(self, obj):
        if obj.create_status == ImageCreateRecord.STATUS_SUCCESS:
            return f"{(obj.updated_at - obj.created_at).seconds}秒"
        return ""
