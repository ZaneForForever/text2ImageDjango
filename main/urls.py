import queue
import django

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse, HttpRequest
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from util.loo import Loo




def a(request: HttpRequest):
    # request.path_info
    print("tianshuo print")
    
    Loo.debug("loo tianshuo")
    # django.logger.info("django.logger.info tianshuo222")
    # django.logging.error("django.logger.info tianshuo222")
    # django.loggi
    return HttpResponse("welcome to ai")


def AuthTemp(r):
    return HttpResponse("01cbdacbaae87115f0838621810957b0")


urlpatterns = [
    path("", a),
    # admin urls
    path("wx/", include("wx.urls")),
    path("ai/", include("ai.urls")),
    path("voice/", include("voice.urls")),
    path("m/", admin.site.urls),
    path("remoteLog/", include("remoteLog.urls")),
    path("88Mkl1XsqH.txt/", AuthTemp),
]

urlpatterns += staticfiles_urlpatterns()


urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
