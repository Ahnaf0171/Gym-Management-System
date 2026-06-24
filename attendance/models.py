from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Attendance(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="attendances",
    )
    gym_branch = models.ForeignKey(
        "gym_branches.GymBranch",
        on_delete=models.PROTECT,
        related_name="attendances",
    )
    check_in = models.DateTimeField(auto_now_add=True)
    check_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-check_in"]
        indexes = [
            models.Index(fields=["member", "check_in"]),
            models.Index(fields=["gym_branch", "check_in"]),
        ]

    def clean(self):
        super().clean()
        if self.member_id:
            if self.member.role != "member":
                raise ValidationError({"member": "Only members can have attendance."})
            if self.gym_branch_id and self.member.gym_branch_id != self.gym_branch_id:
                raise ValidationError({"gym_branch": "Member does not belong to this branch."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.email} - {self.check_in.date()}"