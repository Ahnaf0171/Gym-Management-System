from rest_framework import mixins, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Attendance
from .serializers import AttendanceSerializer
from accounts.models import User
from accounts.permissions import role_required


class AttendanceViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AttendanceSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), role_required(User.MEMBER)()]
        if self.action in ("update", "partial_update"):
            return [permissions.IsAuthenticated(), role_required(User.MEMBER)()]
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), role_required(User.SUPER_ADMIN, User.MANAGER)()]
        return [permissions.IsAuthenticated(), role_required(User.SUPER_ADMIN, User.MANAGER, User.TRAINER)()]

    def get_queryset(self):
        user = self.request.user
        qs = Attendance.objects.select_related("member", "gym_branch")

        if user.role == User.SUPER_ADMIN:
            return qs
        if user.role in (User.MANAGER, User.TRAINER):
            return qs.filter(gym_branch_id=user.gym_branch_id)
        if user.role == User.MEMBER:
            return qs.filter(member_id=user.id)

        return Attendance.objects.none()

    def perform_create(self, serializer):
        serializer.save(member=self.request.user, gym_branch=self.request.user.gym_branch,
    )

    def perform_update(self, serializer):
        serializer.save(check_out=timezone.now())