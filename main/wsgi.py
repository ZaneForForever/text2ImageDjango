"""
WSGI config for main project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


from util.loo import Loo

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

application = get_wsgi_application()

from main import settings
if settings.is_online():
    Loo.info("当前是线上环境2024-01-10-16:39")
else:
    Loo.info("当前是本地环境66")
