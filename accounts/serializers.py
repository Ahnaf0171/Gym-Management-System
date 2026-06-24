from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User
from gym_branches.models import GymBranch


class UserReadSerializer(serializers.ModelSerializer):
    gym_branch_name = serializers.CharField(source="gym_branch.name", read_only=True)
    trainer_email = serializers.EmailField(source="trainer.email", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "mobile_number", "gender", "age", "profile_picture",
            "role", "gym_branch", "gym_branch_name", "trainer", "trainer_email",
            "created_at"
        ]
        read_only_fields = [
            "id", "email", "mobile_number", "role", "gym_branch", "gym_branch_name",
            "trainer_email", "created_at"
        ]

class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    mobile_number = serializers.CharField(
        required=True,
        max_length=15,
        min_length=11,
    )

    class Meta:
        model = User
        fields = ["username", "email", "gender", "age", "profile_picture", "mobile_number", "password"]

    def validate_mobile_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Mobile number must contain only digits.")
        return value

    def validate(self, attrs):
        updater = self.context["request"].user
        target = self.instance

        is_self_update = updater.id == target.id

        if not is_self_update:
            if updater.role == User.MANAGER:
                if target.gym_branch_id != updater.gym_branch_id:
                    raise serializers.ValidationError(
                        "You can only update users in your branch."
                    )
                if target.role not in (User.TRAINER, User.MEMBER):
                    raise serializers.ValidationError(
                        "Manager can only update Trainer or Member."
                    )

            if updater.role == User.MEMBER:
                raise serializers.ValidationError(
                    "You can only update your own profile."
                )

        if "password" in attrs and not is_self_update:
            raise serializers.ValidationError(
                {"password": "You can only change your own password."}
            )

        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save(update_fields=["password"])
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    mobile_number = serializers.CharField(
        required=True,
        max_length=15,
        min_length=11,
    )
    gym_branch = serializers.PrimaryKeyRelatedField(
        queryset=GymBranch.objects.all(),
        required=False,
        allow_null=True
    )
    trainer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="trainer"),
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ["email", "password", "role", "mobile_number", "gym_branch", "trainer"]

    def validate_mobile_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Mobile number must contain only digits.")
        return value

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

            attrs["gym_branch"] = creator.gym_branch

            if role == User.TRAINER:
                trainer_count = User.objects.filter(
                    gym_branch=creator.gym_branch,
                    role=User.TRAINER,
                    is_active=True
                ).count()
                if trainer_count >= 3:
                    raise serializers.ValidationError(
                        {"role": "This branch already has 3 trainers."}
                    )

            if role == User.MEMBER:
                trainer = attrs.get("trainer")
                if not trainer:
                    raise serializers.ValidationError({"trainer": "Trainer is required for a Member."})
                if trainer.gym_branch_id != creator.gym_branch_id:
                    raise serializers.ValidationError({"trainer": "Trainer must be from your branch."})

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