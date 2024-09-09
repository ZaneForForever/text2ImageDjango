

import json
from django.contrib import admin
from ai.models.ai_image_record import ImageCreateRecord

from ai.models.webhook_record import WebhookRecord
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from util import model_util


def registerAdmin():
    print(__file__ + "引入成功")


@admin.register(WebhookRecord)
class WebhookRecordAdmin(admin.ModelAdmin):

    list_display = ['id', "image_create_record_display", 'request_ip', 'request_type', 'request_path',  'has_imageUrl',
                    'originatingMessageId', 'buttonMessageId', 'created_at']

    readonly_fields = list_display+['updated_at', 'deleted_at']

    search_fields = ['originatingMessageId', 'buttonMessageId']

    @admin.display(description='图片记录ID')
    def image_create_record_display(self, obj):

        if obj.originatingMessageId is None or obj.originatingMessageId == "":
            return "-"

        r: ImageCreateRecord = ImageCreateRecord.objects.filter(
            message_id=obj.originatingMessageId).first()
        if r is None:
            return "-"
        change_url = model_util.get_model_change_url(r)

        return mark_safe(f"<a href='{change_url}'>{r.id}</a>")

    @admin.display(description='是否包含图片')
    def has_imageUrl(self, obj):

        result = False

        if obj.request_text is not None and obj.request_text.startswith("b'") and obj.request_text.endswith("'"):
            obj.request_text = obj.request_text[2:-1]

        try:
            o = json.loads(obj.request_text.encode("utf-8"))

        except:
            o = []
            pass
        key = "image_url"
        if key in o and o[key] is not None and o[key] != "":
            result = True

        if not result:

            return format_html("""<img src="/static/admin/img/icon-no.svg" alt="False">""")
        else:
            return format_html("""<img src="/static/admin/img/icon-yes.svg" alt="True">""")
