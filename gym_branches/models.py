from django.db import models

class GymBranch(models.Model):
    name = models.CharField(max_length=200)
    location = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Gym Branches"

    def __str__(self):
        return self.name
