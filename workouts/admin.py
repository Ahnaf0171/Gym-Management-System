from django.contrib import admin
from .models import WorkoutPlan, WorkoutTask

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "gym_branch", "created_by", "created_at")
    list_filter = ("gym_branch", "created_at")
    search_fields = ("title", "description", "created_by__email", "gym_branch__name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("gym_branch", "created_by")

@admin.register(WorkoutTask)
class WorkoutTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "workout_plan", "member", "status", "due_date", "created_at")
    list_filter = ("status", "due_date", "created_at")
    search_fields = ("member__email", "workout_plan__title")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("workout_plan", "member", "workout_plan__gym_branch")
