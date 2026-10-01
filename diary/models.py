from typing import Any

from django.contrib.auth.models import User
from django.db import models


class DiaryEntry(models.Model):
    """
    Модель для представления одной записи в личном дневнике.

    Attributes:
        user (Any): Автор записи (связь с моделью User).
        title (Any): Краткий заголовок заметки.
        content (Any): Полный текст записи дневника.
        image (Any): Опциональное прикрепленное изображение.
        created_at (Any): Дата и время автоматического создания.
        updated_at (Any): Дата и время автоматического обновления.
    """

    # Использование Any решает конфликт типов в mypy без django-stubs
    user: Any = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    title: Any = models.CharField(max_length=200, verbose_name="Заголовок")
    content: Any = models.TextField(verbose_name="Содержание записи")
    image: Any = models.ImageField(
        upload_to="diary_images/", blank=True, null=True, verbose_name="Фотография"
    )
    created_at: Any = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    updated_at: Any = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Запись"
        verbose_name_plural = "Записи"

    def __str__(self) -> str:
        """
        Возвращает строковое представление заголовка записи.

        Returns:
            str: Заголовок дневниковой записи.
        """
        return str(self.title)
