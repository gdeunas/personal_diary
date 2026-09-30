from django import forms

from .models import DiaryEntry


class DiaryEntryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        fields = ["title", "content", "image"]  # Добавили image
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите заголовок записи",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Как прошёл ваш день?",
                }
            ),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }
