

from django.contrib import admin

from ai.models.prompt_example import PromptExampleImageModel


def registerAdmin():
    print(__file__ + "引入成功")


@admin.register(PromptExampleImageModel)
class PromptExampleImageModelAdmin(admin.ModelAdmin):
    raw_id_fields = ("create_image_record",)
    pass
