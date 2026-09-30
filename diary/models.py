from django.contrib.auth.models import User
from django.db import models


class DiaryEntry(models.Model):
    user: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    title: models.CharField = models.CharField(max_length=200, verbose_name="Заголовок")
    content: models.TextField = models.TextField(verbose_name="Содержание записи")
    image: models.ImageField = models.ImageField(
        upload_to="diary_images/", blank=True, null=True, verbose_name="Фотография"
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления"
    )

    class Meta:
        ordering = ["-created_at"]  # Сначала новые записи
        verbose_name = "Запись"
        verbose_name_plural = "Записи"

    def __str__(self) -> str:
        return str(self.title)
