from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Админка для кастомной модели User.
    Наследуется от BaseUserAdmin, но адаптирована под email-логин.
    """
    list_display = ("email", "role", "is_staff", "is_active", "created_at")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email",)
    ordering = ("-created_at",)

    # Поля для формы редактирования
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личная информация", {"fields": ("first_name", "last_name")}),
        ("Права", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "date_joined", "created_at")}),
    )

    # Поля для формы создания
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role"),
        }),
    )

    readonly_fields = ("created_at", "last_login", "date_joined")