from rest_framework import serializers
from .models import Attendance
from django.utils import timezone

class AttendanceSerializer(serializers.ModelSerializer):
    member_email = serializers.EmailField(source="member.email", read_only=True)
    gym_branch_name = serializers.CharField(source="gym_branch.name", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id", "member", "member_email",
            "gym_branch", "gym_branch_name",
            "check_in", "check_out",
        ]
        read_only_fields = ["id", "member", "member_email", "gym_branch", "gym_branch_name", "check_in"]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        is_update = self.instance is not None

        if is_update:
            allowed = {"check_out"}
            extra_fields = set(attrs.keys()) - allowed
            if extra_fields:
                raise serializers.ValidationError("Only check_out can be updated.")
            return attrs

        member = user
        branch = member.gym_branch
        today = timezone.now().date()

        daily_count = Attendance.objects.filter(
            member=member,
            check_in__date=today,
        ).count()

        if daily_count >= 3:
            raise serializers.ValidationError(
                "You have reached the maximum check-ins (3) for today."
            )

        already_checked_in = Attendance.objects.filter(
            member=member,
            check_in__date=today,
            check_out__isnull=True,
        ).exists()

        if already_checked_in:
            raise serializers.ValidationError("Already checked in. Please check out first.")

        attrs["member"] = member
        attrs["gym_branch"] = branch
        return attrs