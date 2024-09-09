
from django.contrib import admin

from ai.models.download_task import DownloadTask
from django.utils.html import format_html, mark_safe

from ai.multi_progress import download_image_progress

from django.core.cache import cache

from util import model_util
def registerAdmin():
    print(__file__ + "引入成功")


@admin.register(DownloadTask)
class DownloadTaskAdmin(admin.ModelAdmin):
    list_display = ('id',  'image_create_record_display',
                    'download_status', 'start_time', 'finish_time', 'download_duration','from_url_display',)
    pass

    readonly_fields = ('created_at', 'updated_at', 'deleted_at')

    actions = ['re_download']

    @admin.display(description='图片记录ID')
    def image_create_record_display(self, obj):
        
        if obj.image_create_record is None:
            return "-"
        
        change_url=model_util.get_model_change_url(obj.image_create_record)

        return mark_safe(f"<a href='{change_url}'>{obj.image_create_record.id}</a>")
    
    @admin.display(description='来源')
    def from_url_display(self, obj):
        if obj.from_url is None or obj.from_url == "":
            return f"-"
        return format_html(f"<a href='{obj.from_url}' target='_blank'>点击新标签打开查看</a>")

    @admin.display(description='耗时')
    def download_duration(self, obj):
        obj: DownloadTask = obj
        if obj.download_status == DownloadTask.STATUS_DOWNLOADING:
            return f"{cache.get(obj.get_redis_key())}%"
        if obj.download_status == DownloadTask.STATUS_SUCCESS and obj.finish_time is not None and obj.start_time is not None:
            return f"{(obj.finish_time - obj.start_time).seconds}秒"

        return ""

    @admin.action(description='重新下载')
    def re_download(self, request, queryset):

        for obj in queryset:
            # obj.download_status = DownloadTask.STATUS_INIT
            # obj.save()
            download_image_progress.download_background(obj.id)
        pass
