
from django.urls import reverse

from django.contrib.contenttypes.models import ContentType

def get_model_change_url(obj)->str:
    content_type = ContentType.objects.get_for_model(obj)
    url = reverse('admin:%s_%s_change' % (content_type.app_label, content_type.model), args=[obj.id])
     
    return url
    pass