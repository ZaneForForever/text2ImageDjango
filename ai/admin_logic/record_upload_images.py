

import json
from django.contrib import admin
from ai.models.ai_image_record import ImageCreateRecord
from ai.models.record_upload_image import RecordUploadImage

from ai.models.webhook_record import WebhookRecord
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from main import settings
from util import model_util
from django.template.loader import render_to_string


def registerAdmin():
    print(__file__ + "引入成功")


@admin.register(RecordUploadImage)
class RecordUploadImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'wx_user',  "display_upload_image", 'source_width',
                    'source_height', 'scale_width', 'scale_height', 'created_at']
    pass

    search_fields = [ 'wx_user__id']
    
    @admin.display(description='图片')
    def display_upload_image(self, o):
        o: RecordUploadImage = o
        if o.source_image is None or o.source_image == "":
            return "-"
       
        image_urls = [{
            "url": o.scale_image.url,
            "big_url": o.source_image.url,
        }]
        
        # print(image_urls)
    
        
         
        
        return render_to_string("ai/list_field/images.html", {"images": image_urls, "task": o, "width": 100, "img_width": 100})
