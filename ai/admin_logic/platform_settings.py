

from typing import Any
from django.contrib import admin

from ai.models.platform_settings import PlatformSettingModel

import base64


def registerAdmin():
    print(__file__ + "引入成功")


@admin.register(PlatformSettingModel)
class PlatformSettingModelAdmin(admin.ModelAdmin):

    list_display = ['id',  'name', 'code', 'value_str',
                    'value_int',  'value_bool', 'updated_at']

    list_editable = ['value_str', 'value_int', 'value_bool']

    def get_queryset(self, request):

        PlatformSettingModel.InitDefaultSettings()

        return super().get_queryset(request).filter(deleted_at=None)

 
