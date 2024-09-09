

from django.urls import path
from voice import api


urlpatterns = [
    path("type/list", api.VoiceTypeList, name="VoiceTypeList"),
    path("create", api.text2Voice, name="text2Voice"),
    path("user/records", api.UserVoiceRecords, name="UserVoiceRecords"),
]
