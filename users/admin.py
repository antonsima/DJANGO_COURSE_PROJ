from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User

# Проверяем и отменяем регистрацию только если модели уже зарегистрированы
try:
    from allauth.account.models import EmailAddress

    admin.site.unregister(EmailAddress)
except (ImportError, admin.sites.NotRegistered):
    pass

try:
    from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken

    admin.site.unregister(SocialAccount)
    admin.site.unregister(SocialApp)
    admin.site.unregister(SocialToken)
except (ImportError, admin.sites.NotRegistered):
    pass


# Кастомный UserAdmin для вашей модели User
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "show_groups",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name")}),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Важные даты", {"fields": ("last_login",)}),  # Убрали date_joined отсюда
    )

    readonly_fields = ("date_joined", "last_login")  # Добавляем поля только для чтения

    filter_horizontal = ("groups", "user_permissions")

    def show_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])

    show_groups.short_description = "Группы"


# Регистрация модели User с кастомным UserAdmin
admin.site.register(User, CustomUserAdmin)


# Улучшенный интерфейс для управления группами
class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ["permissions"]


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
