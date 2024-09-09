from django.db import models

# Create your models here.


from django.db import models
from voice import voice_cache

from wx.models.base_model import BaseModel
from wx.models.wx_user_model import WxUser


class VoiceCreateRecord(BaseModel):
    class Meta:
        db_table = "z_voice_create_record"
        verbose_name = "语音创建记录"
        verbose_name_plural = verbose_name
        pass

    voice_id = models.CharField(
        verbose_name="voice_id", max_length=50, null=False, blank=False)

    wx_user = models.ForeignKey(to=WxUser, on_delete=models.DO_NOTHING,
                                verbose_name="用户", related_name="user_record_voice")

    text = models.TextField(verbose_name="文本", null=True, blank=True)
    voice_url = models.CharField(
        verbose_name="语音url", max_length=255, null=True, blank=True)

    is_custom = models.BooleanField(verbose_name="是否个性化", default=False)

    speech_rate = models.DecimalField(
        verbose_name="语速", default=0, max_digits=3, decimal_places=2)

    def ToJsonObj(self):
        result = {
            "id": self.id,
            "text": self.text,
            "voice_url": self.voice_url,
            "voice": voice_cache.getVoiceCache(self.is_custom, self.voice_id),
            "is_custom": self.is_custom,
            "speech_rate": self.speech_rate,

            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "未知",
        }
        v_o = result['voice'] if result['voice'] else {}
        if self.speech_rate == 0:
            speed_text=f"正常速度"
        else:
            speed_text=f"{self.speech_rate}倍速"
            
        if v_o:
            display_text = f"{v_o['name']}/{v_o['class_name']}/{speed_text}"
            
            result["display_text"] = display_text
        else:
            result["display_text"] = "未知"

        # if self.is_custom:
        #     v=VoiceTypeUserCustomModel.objects.filter(
        #         voice_id=self.voice_id).first()
        #     result["voice"] = v.ToJsonObj()  if v else None
        # else:
        #     v=VoiceTypeModel.objects.filter(
        #         voice_id=self.voice_id).first()
        #     result["voice"] = v.ToJsonObj() if v else None
        return result
    pass


class VoiceTypeUserCustomModel(BaseModel):
    class Meta:
        db_table = "z_voice_type_user_custom"
        verbose_name = "语音(用户自定义)"
        verbose_name_plural = verbose_name
        pass
    name = models.CharField(
        verbose_name="名称", max_length=255, null=True, blank=True)
    voice_id = models.CharField(
        verbose_name="voice_id", max_length=50, null=False, blank=False)

    wx_user = models.ForeignKey(to=WxUser, on_delete=models.DO_NOTHING,
                                verbose_name="用户", related_name="user_custom_voice")
    pass

    def ToJsonObj(self):
        return {
            "name": self.name,
            "voice_id": self.voice_id,
        }


class VoiceTypeModel(BaseModel):
    class Meta:
        db_table = "z_voice_type"
        verbose_name = "语音(平台)"
        verbose_name_plural = verbose_name
        pass

    name = models.CharField(
        verbose_name="人物名称", max_length=255, null=False, blank=False)

    voice_id = models.CharField(
        verbose_name="voice_id",  null=False, blank=False, max_length=50)

    class_name = models.CharField(
        verbose_name="类型", max_length=255, null=True, blank=True)

    adapt_scense = models.CharField(
        verbose_name="适用场景", max_length=255, null=True, blank=True)

    adapt_language = models.CharField(
        verbose_name="适用语言", max_length=255, null=True, blank=True)

    is_adatpt_er = models.BooleanField(verbose_name="是否适用儿话音", default=False)

    # example_voice=models.
    example_voice = models.CharField(
        verbose_name="示例语音", max_length=255, null=True, blank=True)

    sort = models.IntegerField(verbose_name="排序", default=0)

    avatar = models.ImageField(
        verbose_name="头像", null=True, blank=True, upload_to="voice/avatar")

    def ToJsonObj(self):
        return {
            "id": self.id,
            "name": self.name,
            "voice_id": self.voice_id,
            "class_name": self.class_name,
            "adapt_scense": self.adapt_scense,
            "adapt_language": self.adapt_language,
            "is_adatpt_er": self.is_adatpt_er,
            "example_voice": self.example_voice,
            "avatar": self.avatar.url if self.avatar else None,

        }
