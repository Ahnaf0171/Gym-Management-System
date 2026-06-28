from rest_framework import viewsets, mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserReadSerializer, UserCreateSerializer, UserUpdateSerializer, LoginSerializer
from accounts.permissions import role_required
from gym_branches.models import GymBranch
from workouts.models import WorkoutPlan, WorkoutTask
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from django.db import models

class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == User.SUPER_ADMIN:
            return Response({
                "total_branches": GymBranch.objects.count(),
                "total_managers": User.objects.filter(role=User.MANAGER, is_active=True).count(),
                "total_trainers": User.objects.filter(role=User.TRAINER, is_active=True).count(),
                "total_members": User.objects.filter(role=User.MEMBER, is_active=True).count(),
            })

        if user.role == User.MANAGER:
            return Response({
                "total_trainers": User.objects.filter(role=User.TRAINER, gym_branch=user.gym_branch, is_active=True).count(),
                "total_members": User.objects.filter(role=User.MEMBER, gym_branch=user.gym_branch, is_active=True).count(),
                "total_workout_plans": WorkoutPlan.objects.filter(gym_branch=user.gym_branch).count(),
            })

        if user.role == User.TRAINER:
            tasks = WorkoutTask.objects.filter(workout_plan__created_by=user)
            return Response({
                "total_workout_plans": WorkoutPlan.objects.filter(created_by=user).count(),
                "total_tasks": tasks.count(),
                "pending_tasks": tasks.filter(status="pending").count(),
                "in_progress_tasks": tasks.filter(status="in_progress").count(),
                "completed_tasks": tasks.filter(status="completed").count(),
            })

        if user.role == User.MEMBER:
            tasks = WorkoutTask.objects.filter(member=user)
            return Response({
                "total_tasks": tasks.count(),
                "pending_tasks": tasks.filter(status="pending").count(),
                "in_progress_tasks": tasks.filter(status="in_progress").count(),
                "completed_tasks": tasks.filter(status="completed").count(),
            })

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserReadSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

class PublicTrainersByBranchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        branches = GymBranch.objects.prefetch_related(
            models.Prefetch(
                "users",
                queryset=User.objects.filter(role=User.TRAINER, is_active=True),
                to_attr="trainers"
            )
        )

        data = [
            {
                "branch_id": branch.id,
                "branch_name": branch.name,
                "trainers": [
                    {
                        "id": t.id,
                        "full_name": t.username or t.email,
                        "email": t.email,
                        "profile_picture": request.build_absolute_uri(t.profile_picture.url) if t.profile_picture else None,
                    }
                    for t in branch.trainers
                ]
            }
            for branch in branches
            if branch.trainers  
        ]

        return Response(data)
    
class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin, 
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = User.objects.select_related("gym_branch", "trainer").filter(is_active=True)
        user = self.request.user

        if user.role == User.SUPER_ADMIN:
            qs = qs.filter(Q(id=user.id) | ~Q(role=User.SUPER_ADMIN))
        elif user.role == User.MANAGER:
            qs = qs.filter(
                Q(id=user.id) |
                (Q(gym_branch_id=user.gym_branch_id) & ~Q(role=User.MANAGER))
            )
        elif user.role == User.TRAINER:
            qs = qs.filter(Q(id=user.id) | Q(trainer_id=user.id))
        elif user.role == User.MEMBER:
            qs = qs.filter(id=user.id)
        else:
            return User.objects.none()

        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(email__icontains=search)

        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer       
        return UserReadSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), role_required(User.SUPER_ADMIN, User.MANAGER)()]
        if self.action in ("update", "partial_update"):
            return [permissions.IsAuthenticated()]
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), role_required(User.SUPER_ADMIN, User.MANAGER)()]
        if self.action in ("list", "retrieve"):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        instance = self.get_object()
        
        if request.user.role == User.MEMBER and instance.id != request.user.id:
            return Response(
                {"detail": "You can only update your own profile."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserReadSerializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            return Response(
                {"detail": "You cannot delete your own account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.role == User.MANAGER:
            if instance.gym_branch_id != request.user.gym_branch_id:
                return Response(
                    {"detail": "You can only delete users from your own branch."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        try:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"detail": "Cannot delete this user. They may have related data."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        return Response(UserReadSerializer(request.user).data, status=status.HTTP_200_OK)
