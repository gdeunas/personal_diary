import os

from celery import Celery

# Устанавливаем настройки Django по умолчанию для утилиты celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Читаем конфигурацию из settings.py с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находим и регистрируем таски в приложениях Django
app.autodiscover_tasks()
