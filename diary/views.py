from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import DiaryEntry
from .forms import DiaryEntryForm
from django.db.models import Q  # Импортируем Q для сложного поиска
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as login_user


@login_required
def entry_list(request):
    """Просмотр записей + поиск"""
    entries = DiaryEntry.objects.filter(user=request.user)

    # Получаем текст из поисковой строки
    search_query = request.GET.get("search", "")
    if search_query:
        # Ищем совпадения в заголовке ИЛИ содержимом без учета регистра
        entries = entries.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )

    return render(
        request,
        "diary/entry_list.html",
        {"entries": entries, "search_query": search_query},
    )


@login_required
def entry_detail(request, pk):
    """Детальный просмотр одной записи"""
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    return render(request, "diary/entry_detail.html", {"entry": entry})


@login_required
def entry_create(request):
    """Создание записи с поддержкой фото"""
    if request.method == "POST":
        form = DiaryEntryForm(request.POST, request.FILES)  # Добавили request.FILES
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect("entry_list")
    else:
        form = DiaryEntryForm()
    return render(
        request, "diary/entry_form.html", {"form": form, "title": "Новая запись"}
    )


@login_required
def entry_edit(request, pk):
    """Редактирование записи с поддержкой фото"""
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    if request.method == "POST":
        form = DiaryEntryForm(
            request.POST, request.FILES, instance=entry
        )  # Добавили request.FILES
        if form.is_valid():
            form.save()
            return redirect("entry_detail", pk=entry.pk)
    else:
        form = DiaryEntryForm(instance=entry)
    return render(
        request,
        "diary/entry_form.html",
        {"form": form, "title": "Редактировать запись"},
    )


@login_required
def entry_delete(request, pk):
    """Удаление записи"""
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    if request.method == "POST":
        entry.delete()
        return redirect("entry_list")
    return render(request, "diary/entry_confirm_delete.html", {"entry": entry})


def register(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('entry_list')  # Если уже залогинен, отправляем на главную

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login_user(request, user)  # Автоматический вход после регистрации
            return redirect('entry_list')
    else:
        form = UserCreationForm()
    return render(request, 'diary/register.html', {'form': form})
