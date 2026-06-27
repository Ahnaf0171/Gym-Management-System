from rest_framework import serializers
from .models import GymBranch
from django.db.models import Prefetch
from accounts.models import User

class GymBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymBranch
        fields = ["id", "name", "location", "created_at"]
        read_only_fields = ["id", "created_at"]


class PublicGymBranchSerializer(serializers.ModelSerializer):
    manager_email = serializers.SerializerMethodField()
    manager_phone = serializers.SerializerMethodField()

    class Meta:
        model = GymBranch
        fields = ["id", "name", "location", "manager_email", "manager_phone"]

    def get_manager_email(self, obj):
        managers = getattr(obj, 'managers', [])
        return managers[0].email if managers else None

    def get_manager_phone(self, obj):
        managers = getattr(obj, 'managers', [])
        return managers[0].mobile_number if managers else None