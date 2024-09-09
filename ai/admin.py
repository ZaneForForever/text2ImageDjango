from django.contrib import admin

from ai.admin_logic import crontab_record_admin, download_task, image_record, params_config_admin, platform_settings, prompt_example_image_admin, record_upload_images, record_webhook, square_article_admin, voice_admin
from util.loo import Loo

# Register your models here.


from .admin_logic import api_key

api_key.registerAdmin()

image_record.registerAdmin()

download_task.registerAdmin()


record_webhook.registerAdmin()


params_config_admin.registerAdmin()

record_upload_images.registerAdmin()

platform_settings.registerAdmin()

crontab_record_admin.registerAdmin()



prompt_example_image_admin.registerAdmin()


square_article_admin.registerAdmin()

