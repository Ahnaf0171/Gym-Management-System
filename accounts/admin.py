from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User

    ordering = ("-created_at",)
    list_display = ("email", "role", "gym_branch", "is_active", "is_staff", "created_at")
    list_filter = ("role", "gym_branch", "is_active", "is_staff")
    search_fields = ("email",)
    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Role & Branch", {"fields": ("role", "gym_branch")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("created_at",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "gym_branch", "is_active", "is_staff"),
        }),
    )
