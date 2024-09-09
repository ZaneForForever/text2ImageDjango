from django.apps import AppConfig

from util import redis_util
class AiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ai"


redis_util.check_connection()