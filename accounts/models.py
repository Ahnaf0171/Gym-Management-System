from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", User.SUPER_ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("gym_branch", None)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    SUPER_ADMIN, MANAGER, TRAINER, MEMBER = "super_admin", "gym_manager", "trainer", "member"
    ROLE_CHOICES = [
        (SUPER_ADMIN, "Super Admin"),
        (MANAGER, "Gym Manager"),
        (TRAINER, "Trainer"),
        (MEMBER, "Member")
    ]

    GENDER_MALE, GENDER_FEMALE = "male", "female"
    GENDER_CHOICES = [
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
    ]

    full_name = models.CharField(max_length=200, blank=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    mobile_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    gym_branch = models.ForeignKey(
        "gym_branches.GymBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="users",
    )
    trainer = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="members",
        limit_choices_to={"role": "trainer"}
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = "email"

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["gym_branch", "role"])]

    def clean(self):
        super().clean()
        if self.role == self.SUPER_ADMIN and self.gym_branch_id is not None:
            raise ValidationError({"gym_branch": "Super Admin cannot have a gym branch."})
        if self.role != self.SUPER_ADMIN and self.gym_branch_id is None:
            raise ValidationError({"gym_branch": "Branch is required for this role."})

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"