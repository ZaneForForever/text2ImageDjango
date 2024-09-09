

from django.urls import path


from ai import views

from ai.api import download_task, params_config, sd_web_ui, square,   webhook

from .api import image, upload
urlpatterns = [
    path("", views.Home, name="home"),
    path("test", views.Test, name="test"),
    path("ajax", views.AjaxPostPrompt, name="AjaxPostPrompt"),

    path("config/tab/icons", params_config.GetTabIcons, name="GetTabIcons"),

    path("config/params", params_config.GetConfigParams, name="ConfigParams"),
    path("config/prompt/example", square.GetPromptExample, name="GetPromptExample"),

    path("upload/image", upload.UploadImage, name="uploadImage"),
    # downlaod tasks
    path("download/tasks", download_task.download_tasks, name="download_tasks"),
    path("download/failed", download_task.download_failed, name="download_failed"),

    path("download/finish", download_task.download_finish, name="download_finish"),


    path("upscale/image", image.upscale_image, name="upscale_image"),



    path("text2image/v2", image.Text2ImageV2, name="Text2imageV2"),

    path("get/async/images", image.get_async_images, name="get_async_images"),






    path("user/create/records", image.UserCreateRecords, name="UserCreateRecords"),

    path("square/publish/image", square.PublishImage, name="PublishImage"),
    path("square/list", square.SquareList, name="SquareList"),

    
 

    path("webhook/thenextleg.io", webhook.TheNextLegWebhook,
         name="TheNextLegWebhook"),

    path("webhook/zhishuyun.com/imageine",
         webhook.zhi_shu_yun_imagine, name="zhi_shu_yun_imagine"),


]

# sd_web_ui
urlpatterns += [

    path("sdWebUi/tasks", sd_web_ui.getSdWebUiTasks, name="getSdWebUiTasks"),
]
