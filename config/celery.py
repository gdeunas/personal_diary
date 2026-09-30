import os

import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Читаем конфигурацию из settings.py с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
