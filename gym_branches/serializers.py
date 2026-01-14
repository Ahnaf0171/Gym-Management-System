from rest_framework import serializers
from .models import GymBranch

class GymBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymBranch
        fields = ["id", "name", "location", "created_at"]
        read_only_fields = ["id", "created_at"]