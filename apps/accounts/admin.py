from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import User, AllowedEmail, OTPCode


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "phone",
        "is_active",
        "is_staff",
        "created_at",
    )
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "phone")
    ordering = ("-created_at",)

    fieldsets = (
        ("Asosiy ma'lumotlar", {"fields": ("username", "email", "password")}),
        ("Shaxsiy ma'lumotlar", {"fields": ("first_name", "last_name", "phone")}),
        (
            "Ruxsatlar",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Muhim sanalar",
            {"fields": ("last_login", "date_joined", "created_at", "updated_at")},
        ),
    )


@admin.register(AllowedEmail)
class AllowedEmailAdmin(ModelAdmin):
    list_display = ("email", "role", "added_by", "created_at")
    search_fields = ("email", "role")
    list_filter = ("role",)
    ordering = ("-created_at",)


@admin.register(OTPCode)
class OTPCodeAdmin(ModelAdmin):
    list_display = ("email", "code", "expires_at", "used", "attempts", "created_at")
    list_filter = ("used",)
    search_fields = ("email", "code")
    ordering = ("-created_at",)
