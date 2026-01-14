from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User
from gym_branches.models import GymBranch

class UserReadSerializer(serializers.ModelSerializer):
    gym_branch_name = serializers.CharField(source="gym_branch.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "role", "gym_branch", "gym_branch_name", "created_at"]
        read_only_fields = fields

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    gym_branch = serializers.PrimaryKeyRelatedField(
        queryset=GymBranch.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ["email", "password", "role", "gym_branch"]

    def validate(self, attrs):
        creator = self.context["request"].user
        role = attrs.get("role")
        branch = attrs.get("gym_branch")

        if creator.role == User.SUPER_ADMIN:
            if role != User.MANAGER:
                raise serializers.ValidationError("Super Admin can only create Gym Managers.")
            if not branch:
                raise serializers.ValidationError({"gym_branch": "Branch is required for a Manager."})
            return attrs

        if creator.role == User.MANAGER:
            if role not in (User.TRAINER, User.MEMBER):
                raise serializers.ValidationError("Manager can only create Trainers or Members.")

            attrs["gym_branch"] = creator.gym_branch  # force same branch (ignore payload)

            if role == User.TRAINER:
                count = User.objects.filter(
                    gym_branch=creator.gym_branch,
                    role=User.TRAINER,
                    is_active=True
                ).count()
                if count >= 3:
                    raise serializers.ValidationError("This branch already has 3 trainers.")
            return attrs

        raise serializers.ValidationError("You are not allowed to create users.")

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].lower()
        password = attrs["password"]

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")

        attrs["user"] = user
        return attrs
