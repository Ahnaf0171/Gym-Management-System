from django.contrib import admin
from .models import GymBranch

@admin.register(GymBranch)
class GymBranchAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "location", "created_at")
    search_fields = ("name", "location")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
