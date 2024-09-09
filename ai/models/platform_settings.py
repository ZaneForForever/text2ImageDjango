
from wx.models.base_model import BaseModel
from django.db import models


class PlatformSettingModel(BaseModel):

    IS_MID_JOURNEY_OPEN = "is_mid_journey_open"
    FORCE_USE_STABILITY_AI = "force_use_stability_ai"
    IS_ZHI_SHU_YUN_SLOW = "is_zhi_shu_yun_slow"

    CODES = [IS_MID_JOURNEY_OPEN, IS_MID_JOURNEY_OPEN, IS_ZHI_SHU_YUN_SLOW]

    class Meta:
        db_table = "z_platform_settings"
        verbose_name = "平台设置"
        verbose_name_plural = verbose_name
        pass

    name = models.CharField(
        max_length=255, verbose_name="名称", null=False, blank=False)
    code = models.CharField(
        max_length=255, verbose_name="Code", null=False, blank=False)
    value_str = models.CharField(
        max_length=255, verbose_name="值(str)", null=True, blank=True)

    value_bool = models.BooleanField(verbose_name="值(开关)", default=False)
    value_int = models.IntegerField(verbose_name="值(int)", default=0)

    sort = models.IntegerField(
        verbose_name="排序", default=0, null=True, blank=True, help_text="越小越靠前")

    remark = models.CharField(
        verbose_name="备注", max_length=255, null=True, blank=True)

    def InitDefaultSettings():

        # for code in PlatformSettingModel.CODES:
        #     PlatformSettingModel.getDefaultSetting(code)

        pass

    # def Get_Value_By_Code(code) -> "PlatformSettingModel":
    #     return PlatformSettingModel.getDefaultSetting(code)

    def getDefaultSetting(code):
        setting, is_new = PlatformSettingModel.objects.get_or_create(code=code)
        print(f"setting: {setting} is_new:{is_new}")
        return setting

    def is_mid_journey_open():
        return PlatformSettingModel.getDefaultSetting(PlatformSettingModel.IS_MID_JOURNEY_OPEN).value_bool

    def is_zhi_shu_yun_slow():
        return PlatformSettingModel.getDefaultSetting(PlatformSettingModel.IS_ZHI_SHU_YUN_SLOW).value_bool
