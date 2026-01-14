from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from gym_branches.models import GymBranch

class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **kwargs):
        branch, _ = GymBranch.objects.get_or_create(
            name="Dhanmondi Branch",
            defaults={"location": "Dhanmondi, Dhaka"},
        )

        def upsert_user(email, password, role, gym_branch=None, is_staff=False, is_superuser=False):
            email = email.strip().lower()
            user, created = User.objects.get_or_create(email=email, defaults={"role": role})
            user.role = role
            user.gym_branch = gym_branch
            user.is_active = True
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.set_password(password)
            user.full_clean()
            user.save()
            return created

        upsert_user("superadmin@gmail.com", "Admin@1234", User.SUPER_ADMIN, None, True, True)
        upsert_user("manager_rakib@gmail.com", "Manager@1234", User.MANAGER, branch, True, False)

        trainer_emails = [
            "trainer_alif@gmail.com",
            "trainer_jabed@gmail.com",
            "trainer_rakib@gmail.com",
        ]

        for email in trainer_emails:
            existing = User.objects.filter(email=email.lower()).first()
            if not existing:
                count = User.objects.filter(gym_branch=branch, role=User.TRAINER, is_active=True).count()
                if count >= 3:
                    self.stdout.write(self.style.WARNING(f"Skipped {email}: branch already has 3 trainers"))
                    continue
            upsert_user(email, "Trainer@1234", User.TRAINER, branch)

        upsert_user("member_nahin@gmail.com", "Member@1234", User.MEMBER, branch)

        self.stdout.write(self.style.SUCCESS("Seed completed"))
