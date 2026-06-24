from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from accounts.models import User
from accounts.permissions import role_required
from .models import WorkoutPlan, WorkoutTask
from .serializers import WorkoutPlanSerializer, WorkoutTaskSerializer


class BaseScopedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    scope_field = None
    allow_member = False

    def scoped(self, qs):
        u = self.request.user
        if u.role == User.SUPER_ADMIN:
            return qs
        if u.role == User.MANAGER:
            return qs.filter(**{self.scope_field: u.gym_branch_id})
        if u.role == User.MEMBER:
            return qs.filter(member_id=u.id) if self.allow_member else qs.none()
        return qs.none()


class WorkoutPlanViewSet(
    BaseScopedViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = WorkoutPlanSerializer
    scope_field = "gym_branch_id"

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), role_required(User.TRAINER, User.SUPER_ADMIN)()]
        return [IsAuthenticated(), role_required(User.SUPER_ADMIN, User.MANAGER, User.TRAINER)()]

    def get_queryset(self):
        qs = WorkoutPlan.objects.select_related("created_by", "gym_branch")
        u = self.request.user

        if u.role == User.SUPER_ADMIN:
            return qs
        if u.role == User.MANAGER:
            return qs.filter(gym_branch_id=u.gym_branch_id)
        if u.role == User.TRAINER:
            return qs.filter(created_by=u)  

        return qs.none()


class WorkoutTaskViewSet(
    BaseScopedViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = WorkoutTaskSerializer
    scope_field = "workout_plan__gym_branch_id"
    allow_member = True

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), role_required(User.TRAINER, User.SUPER_ADMIN)()]
        if self.action in ("update", "partial_update"):
            return [IsAuthenticated(), role_required(User.MEMBER, User.TRAINER, User.SUPER_ADMIN)()]
        if self.action == "destroy":
            return [IsAuthenticated(), role_required(User.TRAINER, User.SUPER_ADMIN)()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = WorkoutTask.objects.select_related(
            "workout_plan", "workout_plan__gym_branch", "member"
        )
        u = self.request.user

        if u.role == User.SUPER_ADMIN:
            return qs
        if u.role == User.MANAGER:
            return qs.filter(workout_plan__gym_branch_id=u.gym_branch_id)
        if u.role == User.TRAINER:
            return qs.filter(workout_plan__created_by=u) 
        if u.role == User.MEMBER:
            return qs.filter(member_id=u.id)

        return qs.none()

    def perform_update(self, serializer):
        if self.request.user.role == User.MANAGER:
            raise PermissionDenied("Managers cannot update workout tasks.")
        serializer.save()