from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

class WorkoutPlan(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_workout_plans",
    )
    gym_branch = models.ForeignKey(
    "gym_branches.GymBranch", 
    on_delete=models.PROTECT,
    related_name="workout_plans",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["gym_branch", "created_at"]),
            models.Index(fields=["created_by", "created_at"]),
        ]

    def clean(self):
        super().clean()
        if self.created_by_id:
            if self.created_by.role != "trainer":
                raise ValidationError({"created_by": "Only trainers can create workout plans."})
            if self.gym_branch_id and self.created_by.gym_branch_id != self.gym_branch_id:
                raise ValidationError({"gym_branch": "Plan must belong to trainer's branch."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        branch_name = self.gym_branch.name if self.gym_branch_id else "No Branch"
        return f"{self.title} - {branch_name}"

class WorkoutTask(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="workout_tasks",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )
    due_date = models.DateField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["member", "status"]),
            models.Index(fields=["workout_plan", "created_at"]),
        ]

    def clean(self):
        super().clean()
        if self.member_id:
            if self.member.role != "member":
                raise ValidationError({"member": "Tasks can only be assigned to members."})
            if self.workout_plan_id:
                plan_branch_id = WorkoutPlan.objects.values_list(
                    "gym_branch_id", flat=True
                ).get(pk=self.workout_plan_id)
                if self.member.gym_branch_id != plan_branch_id:
                    raise ValidationError({"member": "Cannot assign tasks across branches."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        plan_title = self.workout_plan.title if self.workout_plan_id else "No Plan"
        member_email = self.member.email if self.member_id else "No Member"
        return f"{plan_title} → {member_email} [{self.status}]"
    