

import json
from typing import Any, Dict, List, Optional, Tuple
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from ai.cache.cache_helper import CacheHelper
from ai.models.post_params_config import ParamsFieldModel, ParamsFieldValueModel


def registerAdmin():
    print(__file__ + "引入成功")


@admin.register(ParamsFieldValueModel)
class ValueAdmin(admin.ModelAdmin):
    list_filter = ["param_field"]
    list_display = ["id", "param_field", "post_value",
                    "value_display", "order", "bg_img",  "available", "updated_at"]
    list_editable = ["order", "available", "bg_img"]
    
    ordering=["param_field","order"]
    

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        CacheHelper.clear(CacheHelper.platform_config_params)
        return super().save_model(request, obj, form, change)
    pass


class InLineValueAdmin(admin.TabularInline):
    model = ParamsFieldValueModel
    fields = ["post_value", "value_display", "bg_img", "order", "available","display_filter_field"]
    pass

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:

        return super().get_queryset(request).order_by("order")


@admin.register(ParamsFieldModel)
class ParamsFieldModelAdmin(admin.ModelAdmin):

    inlines = [InLineValueAdmin]

    list_display = ["id", "params_display", "params_code", "params_type",
                    "default_value", "order", "is_advanced", "available", "updated_at"]

    fieldsets = (

        ("参数名称", ({"fields": ("params_display",
         "params_code", "params_type", "default_value","display_filter_field")})),

        ("排序", ({"fields": ("available", "is_advanced", "order", "remark")})),
        ("时间", ({"fields": ("created_at", "updated_at")})),

    )

    list_editable = ["order"]

    list_display_links = ["params_display"]

    readonly_fields = ["created_at", "updated_at", "deleted_at"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).filter(available=True).order_by("is_advanced", "order")

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        return super().save_model(request, obj, form, change)

    pass
