from django.contrib import admin

from .models import DiaryEntry


@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    """Конфигурация отображения записей дневника в админ-панели."""

    list_display = ("title", "user", "created_at", "updated_at")
    list_filter = ("created_at", "user")
    search_fields = ("title", "content", "user__username")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
