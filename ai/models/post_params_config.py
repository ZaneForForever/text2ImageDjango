

from wx.models.base_model import BaseModel
from django.db import models


class ParamsFieldModel(BaseModel):

    def default_params():
        params = dict()
        fs = ParamsFieldModel.objects.filter(
            is_advanced=False, available=True).order_by("order")
        for f in fs:
            params[f.params_code] = f.default_value.post_value

        return params

    class Meta:
        db_table = "z_config_params_field"
        verbose_name = "参数字段"
        verbose_name_plural = verbose_name

    params_code = models.CharField(
        max_length=255, verbose_name="字段Code", blank=True, null=True)
    params_display = models.CharField(
        max_length=255, verbose_name="字段显示", blank=True, null=True)

    params_type = models.CharField(
        max_length=255, verbose_name="字段类型", blank=True, null=True)
    order = models.IntegerField(
        verbose_name="排序", default=0, null=False, blank=False, help_text="越小越靠前")

    remark = models.CharField(
        max_length=255, verbose_name="备注", null=True, blank=True)

    available = models.BooleanField(verbose_name="是否可用", default=True)

    is_advanced = models.BooleanField(verbose_name="是否高级参数", default=False)

    default_value = models.ForeignKey(to="ParamsFieldValueModel", related_name="default_value",
                                      on_delete=models.DO_NOTHING, verbose_name="默认值", null=True, blank=True)

    display_filter_field = models.ForeignKey(to="ParamsFieldValueModel", related_name="params_code_display_filter_field",
                                             on_delete=models.DO_NOTHING, verbose_name="根据某一个字段被选择才展示此字段", null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.params_display}"

    def ToJson(self):
        result = {
            # "id": self.id,
            "is_advanced": self.is_advanced,
            "params_code": self.params_code,
            "params_display": self.params_display,
            # "params_type": self.params_type,
            "values": [v.ToJson() for v in self.field_value.filter(available=True).order_by("order")],
        }
        if self.display_filter_field:
            result["display_by"] = self.display_filter_field.ToJsonWithParent()
        return result


class ParamsFieldValueModel(BaseModel):
    class Meta:
        db_table = "z_config_params_field_value"
        verbose_name = "参数字段的值"
        verbose_name_plural = verbose_name

    parent = models.ForeignKey(to="ParamsFieldValueModel", related_name="children",
                               verbose_name="父级", on_delete=models.DO_NOTHING, null=True, blank=True)

    param_field = models.ForeignKey(
        to=ParamsFieldModel, related_name="field_value", on_delete=models.DO_NOTHING, verbose_name="字段")

    post_value = models.CharField(
        max_length=2048, verbose_name="值", null=False, blank=False)

    value_display = models.CharField(
        verbose_name="值的展示", max_length=2048, null=False, blank=False)

    bg_img_url = models.CharField(
        max_length=2048, verbose_name="背景图", null=True, blank=True)

    bg_img = models.ImageField(
        verbose_name="背景图", null=True, blank=True, upload_to="params_config/bg_img")

    available = models.BooleanField(verbose_name="是否可用", default=True)

    order = models.IntegerField(
        verbose_name="排序", default=0, null=False, blank=False, help_text="越小越靠前")

    api_value_extra = models.TextField(
        verbose_name="api额外参数", null=True, blank=True)

    api_negative_extra = models.TextField(
        verbose_name="api反词额外参数", null=True, blank=True,default=None)
    
    display_filter_list_str = models.CharField(
        verbose_name="展示过滤列表", max_length=2048, null=True, blank=True)

    display_filter_field = models.ForeignKey(to="ParamsFieldValueModel", related_name="params_value_display_filter_field",
                                             on_delete=models.DO_NOTHING, verbose_name="根据某一个字段被选择才展示此字段", null=True, blank=True)

    pass

    def ToJson(self):

        display_by = None

        if self.display_filter_field is not None:
            display_by = self.display_filter_field.ToJsonWithParent()

        result = {
            # "id": self.id,
            "post_value": self.post_value,
            "value_display": self.value_display,
            # "bg_img_url": self.bg_img_url,

        }
        if display_by:
            result["display_by"] = display_by
        if self.bg_img:
            result["bg_img"] = self.bg_img.url
        return result

    def ToJsonWithParent(self):
        result = dict()
        result["params_code"] = self.param_field.params_code
        result["post_value"] = self.post_value

        return result
        pass

    def __str__(self) -> str:
        return f"{self.param_field.params_display}:{self.value_display}"
