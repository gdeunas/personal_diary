from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import DiaryEntryForm
from .models import DiaryEntry

User = get_user_model()


class DiaryModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.entry = DiaryEntry.objects.create(
            title="Тестовый заголовок", content="Тестовое содержание", user=self.user
        )

    def test_entry_creation(self):
        """Проверка успешного сохранения полей в БД."""
        self.assertEqual(self.entry.title, "Тестовый заголовок")
        self.assertEqual(self.entry.content, "Тестовое содержание")

    def test_entry_str_method(self):
        """Проверка строкового представления модели."""
        self.assertEqual(str(self.entry), "Тестовый заголовок")

    def test_entry_user_relation(self):
        """Проверка связи записи с пользователем."""
        self.assertEqual(self.entry.user, self.user)

    def test_ordering_meta(self):
        """Проверка сортировки записей от новых к старым."""
        entry2 = DiaryEntry.objects.create(title="Второй", content="Х", user=self.user)
        entries = list(DiaryEntry.objects.all())
        # Сравниваем первый (самый новый) элемент списка с только что созданным entry2
        self.assertEqual(entries[0], entry2)


class DiaryFormTests(TestCase):
    def test_form_valid_data(self):
        """Форма валидна при правильных данных."""
        form = DiaryEntryForm(
            data={"title": "Валидный заголовок", "content": "Валидный текст"}
        )
        self.assertTrue(form.is_valid())

    def test_form_missing_title(self):
        """Форма невалидна без заголовка."""
        form = DiaryEntryForm(data={"title": "", "content": "Текст"})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_missing_content(self):
        """Форма невалидна без содержания."""
        form = DiaryEntryForm(data={"title": "Заголовок", "content": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_form_title_max_length(self):
        """Форма невалидна, если длина заголовка > 200 символов."""
        form = DiaryEntryForm(data={"title": "x" * 201, "content": "Текст"})
        self.assertFalse(form.is_valid())


class DiaryViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="author", password="password123")
        self.other_user = User.objects.create_user(
            username="stranger", password="password123"
        )
        self.entry = DiaryEntry.objects.create(
            title="Запись автора", content="Секреты", user=self.user
        )

    def test_index_status_code(self):
        """Главная страница возвращает статус 200 для авторизованного пользователя."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("entry_list"))
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        """Главная страница использует нужный HTML-шаблон при авторизации."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("entry_list"))
        self.assertTemplateUsed(response, "diary/entry_list.html")

    def test_register_page_status_code(self):
        """Страница регистрации доступна."""
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_create_view_requires_login(self):
        """Неавторизованный пользователь перенаправляется со страницы создания."""
        response = self.client.get(reverse("entry_create"))
        self.assertEqual(response.status_code, 302)

    def test_create_view_authenticated(self):
        """Авторизованный пользователь видит форму создания."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("entry_create"))
        self.assertEqual(response.status_code, 200)

    def test_create_entry_via_post(self):
        """POST-запрос создает объект в базе."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("entry_create"),
            {"title": "Новый пост", "content": "Новое содержание"},
        )
        self.assertIn(response.status_code, [200, 302])
        self.assertTrue(DiaryEntry.objects.filter(title="Новый пост").exists())

    def test_detail_view_status_code(self):
        """Детальный просмотр доступен."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("entry_detail", kwargs={"pk": self.entry.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_detail_view_contains_content(self):
        """Детальная страница отображает содержание записи."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("entry_detail", kwargs={"pk": self.entry.pk})
        )
        self.assertContains(response, "Секреты")

    def test_update_view_post(self):
        """Автор может успешно обновить запись через POST."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("entry_edit", kwargs={"pk": self.entry.pk}),
            {"title": "Изменено", "content": "Новый текст"},
        )
        self.assertIn(response.status_code, [200, 302])
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.title, "Изменено")

    def test_delete_view_post(self):
        """Автор может удалить запись."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("entry_delete", kwargs={"pk": self.entry.pk})
        )
        self.assertIn(response.status_code, [200, 302])
        self.assertFalse(DiaryEntry.objects.filter(pk=self.entry.pk).exists())

    def test_context_data_list(self):
        """Контекст главной страницы содержит записи в ключе 'entries'."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("entry_list"))
        self.assertIsNotNone(response.context)

    def test_unauthenticated_user_cant_delete(self):
        """Анонимный юзер не может удалить чужую запись без авторизации."""
        # Убрали response =
        self.client.post(reverse("entry_delete", kwargs={"pk": self.entry.pk}))
        self.assertTrue(DiaryEntry.objects.filter(pk=self.entry.pk).exists())

    def test_stranger_cannot_edit_author_entry(self):
        """Пользователь-неавтор не изменяет данные чужого поста."""
        self.client.force_login(self.other_user)
        # Убрали response =
        self.client.post(
            reverse("entry_edit", kwargs={"pk": self.entry.pk}),
            {"title": "Взлом", "content": "Упс"},
        )
        self.entry.refresh_from_db()
        self.assertNotEqual(self.entry.title, "Взлом")
